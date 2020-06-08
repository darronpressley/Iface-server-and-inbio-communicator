function isNumberKey(evt)
{
   var charCode = (evt.which) ? evt.which : event.keyCode
   //if minus
    if (charCode === 45)
        return true;
   //if not a number
   if (charCode > 31 && (charCode < 48 || charCode > 57))
        return false;

   return true;
}
function isNumberKeyNoMinus(evt)
{
   var charCode = (evt.which) ? evt.which : event.keyCode
   //if not a number
   if (charCode > 31 && (charCode < 48 || charCode > 57))
        return false;

   return true;
}

function maxNumCheck(object,intMax) {
    var intValue = parseInt(object.value);
    if (object.value > intMax) {
        object.value = intMax.toString();
    } else if (object.value < (0-intMax)) {
        object.value = '-' + intMax.toString();
    }
}

function alertSavedOptions() {
    alert("Device Options have been Saved");
  }

function isNumCommandsNull(commands) {
    if (commands === '' || commands === '0') {
        alert("Number of commands cannot be null or 0 (1 to 1000).");
        return false;
    } else {
        return commands;
    }
}

function toggleCheckBox(object) {
    if (object.checked){
        console.log("true");
        x = object.id;
        if (x.includes("uface")){
            eid = x.replace("uface","");
            eid = "proface" + eid;
            document.getElementById(eid).checked = false;
        } else if (x.includes("proface")) {
            eid = x.replace("proface","");
            eid = "uface" + eid;
            document.getElementById(eid).checked = false;
        }
    } 
}

