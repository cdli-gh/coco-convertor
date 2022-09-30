import json
import os.path

def createFile(annoList,input_file):
    with open(f'{input_file}_to_w3c.w3c.json', 'w', encoding='utf-8') as f:
        json.dump(annoList, f, ensure_ascii=False, indent=4)
    if(os.path.exists(f'{input_file}_to_w3c.w3c.json')):
        print("File converted and saved in current working directory!")

def convert(input_file):
    f = open(input_file+".json")
    cocoData = json.load(f)
    annoList = []
    id = 0

    for key in cocoData:
        if key == "annotations":
            for ele in cocoData[key]:
                id = id + 1
                annoDict = {}
                annoDict["@context"] = "http://www.w3.org/ns/anno.jsonld"
                annoDict["id"] = id
                annoDict["type"] = "Annotation"
                annoDict["body"] = []
                annoDict["body"].append(
                    {
                        "type": "TextualBody",
                        "value": next(
                            iter(
                                item["name"]
                                for item in cocoData["categories"]
                                if item["id"] == ele["category_id"]
                            ),
                            "",
                        ),
                    }
                )
                annoDict["target"] = {"selector": []}
                for links in cocoData["images"]:
                    annoDict["target"]["source"] = links['file_name']
                    break

                # check for ellipse
                if len(ele["segmentation"][0]) == 144 and ele["bbox"][2] != ele["bbox"][3]:
                    rx = str(ele["bbox"][2] / 2)
                    ry = str(ele["bbox"][3] / 2)
                    cx = ele["segmentation"][0][36]
                    cy = ele["segmentation"][0][1]
                    ellipsePath = '<svg><ellipse cx="${cx}" cy="{cy}" rx="${rx}" ry="{ry}"></ellipse></svg>'
                    annoDict["target"]["selector"].append(
                        {
                            "type": "SvgSelector",
                            "value": ellipsePath,
                        }
                    )
                # check for circle
                elif (
                    len(ele["segmentation"][0]) == 144 and ele["bbox"][2] == ele["bbox"][3]
                ):
                    r = str(ele["bbox"][2] / 2)
                    cx = ele["segmentation"][0][36]
                    cy = ele["segmentation"][0][1]
                    circlePath = (
                        '<svg><circle cx="${cx}" cy="{cy}" r="${r}"></circle></svg>'
                    )
                    annoDict["target"]["selector"].append(
                        {
                            "type": "SvgSelector",
                            "value": circlePath,
                        }
                    )
                # check for square/rect
                elif (
                    len(ele["segmentation"][0]) == 8
                    and ele["segmentation"][0][0] == ele["bbox"][0]
                    and ele["segmentation"][0][1] == ele["bbox"][1]
                ):
                    pixels = (
                        str(ele["bbox"][0])
                        + ","
                        + str(ele["bbox"][1])
                        + ","
                        + str(ele["bbox"][2])
                        + ","
                        + str(ele["bbox"][3])
                    )

                    annoDict["target"]["selector"].append(
                        {
                            "type": "FragmentSelector",
                            "conformsTo": "http://www.w3.org/TR/media-frags/",
                            "value": "xywh=pixel:"+pixels,
                        }
                    )
                # check for polygon
                else:
                    pointsList = []
                    totalLen = len(ele["segmentation"][0])
                    n = len(ele["segmentation"][0]) / 2
                    i = 0
                    while i < totalLen:
                        if i == 0:
                            pointsList.append(str(ele["segmentation"][0][i]))
                            i = i + 1
                            continue
                        try:
                            if (
                                ele["segmentation"][0][i] in ele["segmentation"][0]
                                and ele["segmentation"][0][i + 1] in ele["segmentation"][0]
                            ):
                                points = (
                                    str(ele["segmentation"][0][i])
                                    + " "
                                    + str(ele["segmentation"][0][i + 1])
                                )
                                pointsList.append(points)
                                i = i + 2
                        except IndexError:
                            if len(pointsList) - 1 < n:
                                points = (
                                    str(ele["segmentation"][0][i])
                                    + " "
                                    + str(ele["segmentation"][0][i - 1])
                                )
                                pointsList.append(points)
                                pointsList.append(str(ele["segmentation"][0][i]))
                                break
                    if totalLen % 2 != 0:
                        pointsList.append(str(ele["segmentation"][0][totalLen - 1]))

                    svgPoints = ",".join(pointsList)
                    annoDict["target"]["selector"].append(
                        {
                            "type": "SvgSelector",
                            "value": f"<svg><polygon points='{svgPoints}'></polygon></svg>",
                        }
                    )
                annoList.append(annoDict)
    createFile(annoList,input_file)

input_file = input("Enter the file name you want to convert(without extension): ")
if not input_file or ' ' in input_file:
    print("Please enter the name without spaces!")
elif not os.path.exists(f'{input_file}.json'):
    print("Please make sure that the file you want to convert is in the current working directory!")
else:
    convert(input_file)
