function on(x=0) {
      document.getElementById("overlay").style.display = "block";
      switch(x){
        case 't':
          document.getElementsByClassName("task-form")[0].style.display ="block";
          break;
        case 'e':
          document.getElementsByClassName("edit-form")[0].style.display ="block";
          break;
        case 'd':
          document.getElementsByClassName("delete-form")[0].style.display ="block";
          break;
        case 'a':
          document.getElementsByClassName("add-due-form")[0].style.display ="block";
          break;
        case 'et':
          document.getElementsByClassName("edit-task-form")[0].style.display ="block";
          break;
        default:
          document.getElementById("project-form").style.display = "block";
          break;
      }
  }
  
function off(x=0) {
  document.getElementById("overlay").style.display = "none";
  switch(x){
    case 't':
      document.getElementsByClassName("task-form")[0].style.display ="none";
      break;
    case 'e':
      document.getElementsByClassName("edit-form")[0].style.display ="none";
      break;
    case 'd':
      document.getElementsByClassName("delete-form")[0].style.display ="none";
      break;
    case 'a':
      document.getElementsByClassName("add-due-form")[0].style.display ="none";
      break;
    case 'et':
      document.getElementsByClassName("edit-task-form")[0].style.display ="none";
      break;
    default:
      document.getElementById("project-form").style.display = "none";
      break;
  }
}

function setValForDel(pid, ptitle){
  document.getElementById("delete-input").value = pid;
  document.getElementById("project-delete-title").innerHTML = "Are you sure you want to delete " +  ptitle + "!";
}

function setValsForEdit(pid, ptitle, pdue){
  document.getElementById("edit-input").value = pid;
  document.getElementById("edit-title").value = ptitle;
  document.getElementById("edit-due").value = pdue;
}

function setID(pid, elementID){
  document.getElementById(elementID).value = pid;
}

function setValsForEditTask(tid, ttitle, tdescription, status){
  document.getElementById("editTaskName").value = ttitle;
  document.getElementById("editTaskD").value = tdescription;
  document.getElementById("editTaskID").value = tid;
  document.getElementById("editTaskStatus").value = status;
}

function showD(action,tid){
  switch(action){
    case 'show':
      document.getElementById('t'+tid).style.display = 'block';
      document.getElementById('showBtn'+tid).style.display = 'none';
      document.getElementById('hideBtn'+tid).style.display = 'block';
      break;
    case 'hide':
      document.getElementById('t'+tid).style.display = 'none';
      document.getElementById('showBtn'+tid).style.display = 'block';
      document.getElementById('hideBtn'+tid).style.display = 'none';
      break;

  }
}