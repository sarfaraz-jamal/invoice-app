import re


def parse_invoice_form(form):
    invoice_data = {}
    items = {}

    for key, value in form.multi_items():

        # Match:
        # items[0][hsCode]
        # items[1][quantity]
        match = re.match(r"items\[(\d+)\]\[(.+)\]", key)

        if match:
            index = int(match.group(1))
            field = match.group(2)

            if index not in items:
                items[index] = {}

            items[index][field] = value

        else:
            invoice_data[key] = value

    invoice_data["items"] = [
        items[index]
        for index in sorted(items)
    ]

    return invoice_data