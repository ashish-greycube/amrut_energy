frappe.ui.form.on('Issue', {
    refresh: function (frm) {
        frm.page.add_menu_item(__("Start Meeting"), function () {
            frappe.call({
                method: 'amrut_energy.videosdk.create_meeting',
                args: {
                    subject: frm.doc.subject,
                },
                btn: $('.primary-action'),
                freeze: true,
                callback: (r) => {
                    console.log(r)
                    const { message } = r
                    frm.dashboard.add_comment(`Created meeting <a target="_blank" href="${message}">${message}</a>`)
                },
                error: (r) => {
                    console.log(r)
                    frappe.show_alert("Something went wrong please try again");
                }
            })

        });
    }
});

