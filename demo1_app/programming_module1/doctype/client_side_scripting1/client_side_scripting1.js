// Copyright (c) 2026, Demo and contributors
// For license information, please see license.txt

frappe.ui.form.on("Client Side Scripting1", {
// 	refresh(frm) {
//         //frappe.msgprint("Welcome to Client Side Scripting Doctype!");
//         frappe.throw("This is an error");
// 	},
    validate:function(frm){
       // frm.set_value('fullname', frm.doc.firstname + " " + frm.doc.middlename + " " + frm.doc.lastname);
       let row=frm.add_child('family_members1',{
        name1:'Nihitha',
        age:21,
        relation:'Sister'
       })
    }});
