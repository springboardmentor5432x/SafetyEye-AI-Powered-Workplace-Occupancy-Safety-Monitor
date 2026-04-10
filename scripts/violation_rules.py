def check_ppe_violations(person_boxes, ppe_boxes):
    """
    Evaluates if a person is wearing required PPE based on bounding box overlap.
    ppe_boxes should be a dict like {'hardhats': [[x1, y1, x2, y2], ...], 'vests': [...]}
    Returns a list of violation dictionaries for each person.
    """
    violations = []
    
    for px in person_boxes:
        px1, py1, px2, py2 = px
        
        explicit_no_hardhat = False
        explicit_no_vest = False
        explicit_no_mask = False
        
        # Check explicit NO-Hardhat overlap
        for nhx in ppe_boxes.get('no_hardhats', []):
            if is_overlapping(px, nhx):
                explicit_no_hardhat = True
                break
                
        # Check explicit NO-Safety Vest overlap
        for nvx in ppe_boxes.get('no_vests', []):
            if is_overlapping(px, nvx):
                explicit_no_vest = True
                break
                
        # Check explicit NO-Mask overlap
        explicit_no_mask = False
        for nmx in ppe_boxes.get('no_masks', []):
            if is_overlapping(px, nmx):
                explicit_no_mask = True
                break
                
        violations.append({
            'person_box': px,
            'missing_hardhat': explicit_no_hardhat,
            'missing_vest': explicit_no_vest,
            'missing_mask': explicit_no_mask
        })
        
    return violations

def is_overlapping(box1, box2):
    """
    Checks if two bounding boxes [x1, y1, x2, y2] intersect.
    """
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    if x_right < x_left or y_bottom < y_top:
        return False
        
    return True
