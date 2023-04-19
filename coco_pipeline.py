import json
import sys

def createFile(annoList):
    sys.stdout.write(json.dumps(annoList))

def convert(input):
    cocoData = json.loads(input)
    annoList = []
    id = 0
    cocoData = json.loads(cocoData[0])
    for key in cocoData:
        if key == "annotations":
            for ele in cocoData[key]:
                id = id + 1
                annoDict = {}
                annoDict["@context"] = "http://www.w3.org/ns/anno.jsonld"
                annoDict["id"] = str(id)
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
                for item in cocoData["images"]:
                    if item["id"] == ele["image_id"]:
                        annoDict["target"]["source"] = item["file_name"]
                # check for ellipse
                if len(ele["segmentation"][0]) == 144 and ele["bbox"][2] != ele["bbox"][3]:
                    rx = str(ele["bbox"][2] / 2)
                    ry = str(ele["bbox"][3] / 2)
                    cx = ele["segmentation"][0][36]
                    cy = ele["segmentation"][0][1]
                    ellipsePath = f'<svg><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"></ellipse></svg>'
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
                        f'<svg><circle cx="{cx}" cy="{cy}" r="{r}"></circle></svg>'
                    )
                    annoDict["target"]["selector"].append(
                        {
                            "type": "SvgSelector",
                            "value": circlePath,
                        }
                    )
                # check for polygon
                else:
                    pointsList = []
                    totalLen = len(ele["segmentation"][0])
                    i = 0
                    while i < totalLen:
                        if i == 0:
                            pointsList.append(str(ele["segmentation"][0][i]))
                            i = i + 1
                            continue
                        try:
                            points = (
                                str(ele["segmentation"][0][i])
                                + " "
                                + str(ele["segmentation"][0][i + 1])
                            )
                            pointsList.append(points)
                            i = i + 2
                        except IndexError:
                            break
                        pointsList.append(str(ele["segmentation"][0][i]))
                    svgPoints = ",".join(pointsList)
                    annoDict["target"]["selector"].append(
                        {
                            "type": "SvgSelector",
                            "value": f"<svg><polygon points='{svgPoints}'></polygon></svg>",
                        }
                    )
                annoList.append(annoDict)
    createFile(annoList)


if __name__ == '__main__':
    input = sys.stdin.readlines()
    convert(json.dumps(input))