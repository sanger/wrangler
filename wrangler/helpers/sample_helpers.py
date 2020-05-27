import re


def position_contents_for(supplier_sample_id: str):
    return {"content": sample_contents_for(supplier_sample_id)}


def sample_contents_for(supplier_sample_id: str):
    return add_control_sample_if_present({"supplier_name": supplier_sample_id})


def add_control_sample_if_present(sample_record: dict):
    """Adds the information for the control to the sample sample_record if the supplier sample id represents
    a control sample.

    Arguments: 
        sample_record -- Tube sample_record that will be sent to Sequencescape, with the supplier sample id in it

    Returns:
        dict -- the sample_record argument with the added information for the control if required
    """
    supplier_sample_id = sample_record["supplier_name"]
    assert supplier_sample_id
    is_control = control_for(supplier_sample_id)
    if is_control:
        sample_record["control"] = is_control
        sample_record["control_type"] = control_type_for(supplier_sample_id)

    return sample_record


def control_for(supplier_sample_id: str):
    """Checks if a sample received is a control sample.

    Arguments:
        supplier_sample_id -- the supplier sample id of a sample from Cgap Heron

    Returns:
        Boolean -- If the supplier_sample id is a control it returns true, otherwise false
    """
    return bool(re.match(".*control.*", supplier_sample_id, re.IGNORECASE))


def control_type_for(supplier_sample_id: str):
    """Returns the type of control sample for a supplier sample id provided

    Arguments:
        supplier_sample_id -- the supplier sample id of a sample from Cgap Heron

    Returns:
        String -- "Positive" if the supplier_sample id is a positive control, "Negative if is a negative control"
        None if is not a control, or if is not positive or negative
    """
    if re.match(".*positive.*", supplier_sample_id, re.IGNORECASE):
        return "positive"
    if re.match(".*negative.*", supplier_sample_id, re.IGNORECASE):
        return "negative"
    return None
