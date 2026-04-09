class ViolationRuleEngine:
    """
    Checks PPE safety compliance rules using YOLO detections.

    Expected detection format:
    {
        "label": "Person" or "Hardhat" or "Safety Vest",
        "box": [x1, y1, x2, y2],
        "conf": 0.87
    }
    """

    def __init__(self):
        # Minimum box overlap required to treat PPE as belonging to a person
        self.min_iou = 0.1

    def get_iou(self, box1, box2):
        """
        Compute Intersection over Union (IoU) between two boxes.

        IoU helps decide whether a helmet/vest overlaps with a person enough
        to count as being worn.
        """
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        if intersection == 0:
            return 0.0

        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        if union == 0:
            return 0.0

        return intersection / float(union)

    def check_violations(self, detections):
        """
        Check all current detections and return a list of violation messages.
        """
        violations = []
        persons = []
        hardhats = []
        vests = []

        # Split detections by type
        for d in detections:
            label = d["label"]

            if label == "Person":
                persons.append(d)
            elif label == "Hardhat":
                hardhats.append(d)
            elif label == "Safety Vest":
                vests.append(d)
            elif label == "NO-Hardhat" and "Missing Hardhat" not in violations:
                violations.append("Missing Hardhat")
            elif label == "NO-Safety Vest" and "Missing Safety Vest" not in violations:
                violations.append("Missing Safety Vest")

        # No people means no person-level PPE rule to check
        if len(persons) == 0:
            return violations

        # Rule 1: Hardhat check
        if len(hardhats) == 0:
            violations.append("No Hardhat detected on person")
        else:
            for person in persons:
                has_helmet = False

                for helmet in hardhats:
                    # Standard overlap check
                    if self.get_iou(person["box"], helmet["box"]) > self.min_iou:
                        has_helmet = True
                        break

                    # Extra fallback:
                    # If helmet appears in upper region of the person box,
                    # count it as valid even if overlap is small.
                    helmet_top = helmet["box"][1]
                    person_top = person["box"][1]
                    person_bottom = person["box"][3]
                    person_left = person["box"][0]
                    person_right = person["box"][2]
                    person_height = person_bottom - person_top

                    if (
                        helmet_top < person_top + 0.5 * person_height
                        and helmet["box"][0] < person_right
                        and helmet["box"][2] > person_left
                    ):
                        has_helmet = True
                        break

                if not has_helmet and "No Hardhat detected on person" not in violations:
                    violations.append("No Hardhat detected on person")

        # Rule 2: Safety vest check
        if len(vests) == 0:
            violations.append("No Safety Vest detected on person")
        else:
            for person in persons:
                has_vest = False

                for vest in vests:
                    if self.get_iou(person["box"], vest["box"]) > self.min_iou:
                        has_vest = True
                        break

                    # Fallback:
                    # Vest should usually appear in middle/lower upper body area
                    vest_top = vest["box"][1]
                    vest_bottom = vest["box"][3]
                    person_top = person["box"][1]
                    person_bottom = person["box"][3]
                    person_left = person["box"][0]
                    person_right = person["box"][2]
                    person_height = person_bottom - person_top

                    if (
                        vest_top > person_top + 0.2 * person_height
                        and vest_bottom < person_bottom
                        and vest["box"][0] < person_right
                        and vest["box"][2] > person_left
                    ):
                        has_vest = True
                        break

                if not has_vest and "No Safety Vest detected on person" not in violations:
                    violations.append("No Safety Vest detected on person")

        return violations