import json
import sys

def createFile(annoList):
    sys.stdout.write(json.dumps(annoList))

def convert(input_file):
    viaData = json.loads(input_file)
    annoList = []
    id = 0
    viaData = json.loads(viaData[0])
    for key in viaData:
        if key == "_via_img_metadata":
            for ele in viaData[key]:
                for region in viaData[key][ele]["regions"]:
                    annoDict = {}
                    id = id + 1
                    annoDict["@context"] = "http://www.w3.org/ns/anno.jsonld"
                    annoDict["id"] = str(id)
                    annoDict["type"] = "Annotation"
                    annoDict["body"] = []
                    annoDict["target"] = {"selector": []}
                    annoDict["target"]["source"] = viaData[key][ele]["filename"]
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
                                "type": "SvgSelector",
                                "conformsTo": "http://www.w3.org/TR/media-frags/",
                                "value": "xywh=pixel:"+pixels,
                            }
                        )
                    elif (
                        region["shape_attributes"]["name"] == "point"
                    ):
                        r = 4
                        cx = region["shape_attributes"]["cx"]
                        cy = region["shape_attributes"]["cy"]
                        
                        pointPath = (
                            f'<svg><circle cx="{cx}" cy="{cy}" r="{r}"></circle></svg>'
                        )
                        annoDict["target"]["selector"].append(
                            {
                                "type": "SvgSelector",
                                "value": pointPath,
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

    createFile(annoList)

if __name__ == '__main__':
    input = sys.stdin.readlines()
    convert(json.dumps(input))
