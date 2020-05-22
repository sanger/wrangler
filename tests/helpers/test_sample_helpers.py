from wrangler.helpers.sample_helpers import add_control_sample_if_present, control_for, control_type_for

def test_control_for_normal_sample():
    supplier_sample_id = "A sample"
    assert control_for(supplier_sample_id) == False
    assert control_type_for(supplier_sample_id) == None


def test_control_for_positive_control():
    supplier_sample_id = "A sample with positive control and other stuff"
    assert control_for(supplier_sample_id) == True
    assert control_type_for(supplier_sample_id) == "Positive"


def test_control_for_negative_control():
    supplier_sample_id = "a negative control sample"
    assert control_for(supplier_sample_id) == True
    assert control_type_for(supplier_sample_id) == "Negative"


def test_control_for_control():
    supplier_sample_id = "A sample it has a control in it and other stuff"
    assert control_for(supplier_sample_id) == True
    assert control_type_for(supplier_sample_id) == None


def test_set_add_control_sample_if_present():
    record = {"supplier_name": "is a positive control"}
    add_control_sample_if_present(record)
    assert record["control"] == True
    assert record["control_type"] == "Positive"


def test_not_set_control_sample_if_not_present():
    record = {"supplier_name": "is a very positive sample"}
    add_control_sample_if_present(record)
    assert not "control" in record
