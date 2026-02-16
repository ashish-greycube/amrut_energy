let dist = ""
let state = ""
let block = ""

frappe.ui.form.on("Lead", {
    territory(frm) {
        set_territory_type(frm)
    },
    onload(frm) {
        frm.set_query("custom_location_state", (frm) => {
            return {
                "filters": {
                    "custom_territory_type": "State"
                }
            }
        })
        frm.set_query("custom_district", (frm) => {
            return {
                "filters": {
                    "custom_territory_type": "District"
                }
            }
        })
        frm.set_query("custom_block", (frm) => {
            return {
                "filters": {
                    "custom_territory_type": "Block"
                }
            }
        })
    },
    custom_location_state(frm) {
        frm.set_query("custom_district", (frm) => {
            return {
                "filters": {
                    "parent_territory": `${frm.custom_location_state}`,
                    "custom_territory_type": "District"
                }
            }
        })
    },
    custom_district(frm) {
        frm.set_query("custom_block", (frm) => {
            return {
                "filters": {
                    "parent_territory": `${frm.custom_district}`,
                    "custom_territory_type": "Block"
                }
            }
        })
    },
});

const set_territory_type = (frm) => {
    frappe.call({
        method: "amrut_energy.doc_events.populate_location_lead",
        args: {
            doc: frm.doc
        },
        callback: (r) => {

            let list = r.message

            state = list["custom_location_state"]
            dist = list["custom_district"]
            block = list["custom_block"]

            frm.set_value({
                "custom_location_state": state,
                "custom_district": dist,
                "custom_block": block
            })

            frappe.show_alert({
                message: __('Values set succesfully!'),
                indicator: 'green'
            }, 3);

            // console.log(r.exc)
        }
    });
}