import blpapi


def get_curve_members(field_data, field_name="CURVE_MEMBERS"):
    field_blp_name = blpapi.Name(field_name)
    curve_members_e = field_data.getElement(field_blp_name)
    curve_members = [curve_members_e.getValueAsElement(i).getElementAsString("Curve Members")
                     for i in range(curve_members_e.numValues())]
    return curve_members


