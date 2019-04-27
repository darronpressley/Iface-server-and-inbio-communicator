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

function maxLengthCheck(object) {
    console.log(object.value);
    var intValue = parseInt(object.value);
    if (object.value > 23) {
        object.value = '23';
    } else if (object.value < -23) {
        object.value = '-23';
    }
}