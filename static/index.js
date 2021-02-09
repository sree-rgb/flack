document.addEventListener('DOMContentLoaded', () => {


    // Connect to websocket
    const dbutton = document.querySelector('#modalTest');
    dbutton.disabled=true;
    const dbox = document.querySelector('#dname');
    const debugText=document.querySelector('#debug-text')
    document.querySelector('#dname').onkeyup  =  () =>  {
        
        const dname = dbox.value
        
        // const dbutton=document.querySelector('#modalTest')

         document.querySelector('#debug-text').innerHTML = 'test';
           const request = new XMLHttpRequest();
               request.open('POST',  '/dnamecheck');
               request.onload= () => {
                dbutton.disabled=true;
                   const response  = request.responseText;
                   debugText.innerHTML = response;
                   if (dname.length === 0){
                    debugText.style.color="black";
                    dbox.style.border="solid 1px blue";

                   }
                   else if (response === "False"){
                    debugText.style.color="red";
                    dbox.style.border="solid 1px red";
                   }
                   else{
                    debugText.style.color="green";
                    dbox.style.border="solid 1px green"
                    dbutton.disabled=false;
                   }

                   
               };
               const data = new FormData();
                data.append('dname', dname);
               request.send(data);
    }
    // When connected, configure buttons
    // socket.on('connect', () => {

    //     // Each button should emit a "submit vote" event
    //     document.querySelectorAll('button').forEach(button => {
    //         button.onclick = () => {
    //             const selection = button.dataset.vote;
    //             socket.emit('submit vote', {'selection': selection});
    //         };
    //     });
    // });

    // When a new vote is announced, add to the unordered list
    // socket.on('vote totals', data => {
    //     document.querySelector('#yes').innerHTML = data.yes;
    //     document.querySelector('#no').innerHTML = data.no;
    //     document.querySelector('#maybe').innerHTML = data.maybe;
    // });
    //     socket.on('display name', data => {
    //     document.querySelector('#yes').innerHTML = "twat2";
    //     document.querySelector("#modalButton").click();
    //     document.querySelector('#maybe').innerHTML = data.maybe;
    // });

});

