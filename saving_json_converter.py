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
        if key == "_via_img_metadata":
            for ele in cocoData[key]:
                id = id + 1
                annoDict = {}
                annoDict["@context"] = "http://www.w3.org/ns/anno.jsonld"
                annoDict["id"] = id
                annoDict["type"] = "Annotation"
                annoDict["body"] = []
                annoDict["target"] = {"selector": []}
                annoDict["target"]["source"] = cocoData[key][ele]["filename"]

                for region in cocoData[key][ele]["regions"]:
                    annoDict["body"].append(
                        {
                            "type": "TextualBody",
                            "value": region["region_attributes"]["type"]
                        }
                    )
                    # check for ellipse
                    if region["shape_attributes"]["name"] == "ellipse":
                        rx = region["shape_attributes"]["rx"]
                        ry = region["shape_attributes"]["ry"]
                        cx = region["shape_attributes"]["cx"]
                        cy = region["shape_attributes"]["cy"]
                        ellipsePath = f'<svg><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"></ellipse></svg>'
                        annoDict["target"]["selector"].append(
                            {
                                "type": "SvgSelector",
                                "value": ellipsePath,
                            }
                        )
                    # check for circle
                    elif (
                        region["shape_attributes"]["name"] == "circle"
                    ):
                        r = region["shape_attributes"]["r"]
                        cx = region["shape_attributes"]["cx"]
                        cy = region["shape_attributes"]["cy"]
                        
                        circlePath = (
                            f'<svg><circle cx="{cx}" cy="{cy}" r="{r}"></circle></svg>'
                        )
                        annoDict["target"]["selector"].append(
                            {
                                "type": "SvgSelector",
                                "value": circlePath,
                            }
                        )
                    # check for square/rect
                    elif (
                        region["shape_attributes"]["name"] == "rect"
                    ):
                        pixels = (
                            str(region["shape_attributes"]["x"])
                            + ","
                            + str(region["shape_attributes"]["y"])
                            + ","
                            + str(region["shape_attributes"]["width"])
                            + ","
                            + str(region["shape_attributes"]["height"])
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
                        totalLen = len(region["shape_attributes"]["all_points_x"]) + len(region["shape_attributes"]["all_points_y"])
                        i = 0
                        j = 0
                        k = 0
                        while i < totalLen:
                            if i%2 == 0:
                                pointsList.append(str(region["shape_attributes"]['all_points_x'][j]))
                                j = j + 1
                            else:
                                pointsList.append(str(region["shape_attributes"]['all_points_y'][k]))
                                k = k + 1
                            i = i + 1
                                
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
