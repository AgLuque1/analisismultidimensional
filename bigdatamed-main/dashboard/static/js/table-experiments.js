// variable that controls when the edit experiment button has been clicked
var edit_clicked;

/**
 * document ready function, runs functions once the web (DOM) is fully loaded
 */
 $(document).ready(function() {

  debugger;
  // DataTable table_dynamic. Custom paging with Django, Checkbox column in position 2, multishift selection style. The checkbox for selection is in the last column of the table (pos 2).
  var table = $("#table_experiments").DataTable({
    // Pagination, labels and other options
    paging: true,
    language: {
        search: "Buscar:",
        lengthMenu: "Mostrar _MENU_ entradas",
        info: "Mostrando _START_ hasta _END_ de un total de _TOTAL_ entradas",
        paginate: {
            next:       "Siguiente",
            previous:   "Anterior"
        },
    },
    order: [],
    dom: "<'row'<'col-sm-12 col-md-6'f><'col-sm-12 col-md-6'p>>" + "<'row'<'col-sm-12'tr>>" + "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'i>>",
  });

});

/**
 * Function that resets the variable that controls when the edit button has been clicked when the page is shown
 */
window.addEventListener("pageshow", () => {
  edit_clicked = false;
});

/**
 * Function change cursor above rows table_experiments
 */
$('#table_experiments > tbody > tr ').hover(function() {
    $(this).css('cursor','pointer');
});

/**
 * Function changes color  rows select when you click above them in the table_experiments, so we will know that row we have  select.
 * Fill field hidden that it will be send with the form load experiment 
 * Remove class disabled in order to allow send load experiments
 */
$('#table_experiments').on('click', 'tbody tr', function(){

  // if the edit experiment button has not been clicked, select the row and add the highlight to the row
  if (!edit_clicked){
    selectRowManual(this,true)
  }
  
});

/**
 * Function for remove experiment from table
 * We use of SweetAlert2's library with AJAX
 */
$(".experiment-rm").on('click',function(){
    // Get id_exp from click row 
    var id_exp = $(this).parent().parent().children("td.id_exp")[0].innerText; 
   
    Swal.fire({
        title: '¿Seguro que quiere borrar?',
        text: "No podrás deshacer esta acción",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Si, eliminalo',
        preConfirm: async(confirm) => { //confirm is variable return for own sweetAlert2 it value can be ( True or False ) depend Accept or Cancel operation
            return fetch(`ajax/remove-exp-table/${id_exp}`) // Call  Django's view
              .then(response => {
                if (!response.ok) {
                  throw new Error(response.statusText)
                }
                return response.json()
              })
              .catch(error => {
                Swal.showValidationMessage(
                  `Request failed: ${error}`
                )
              })
          },
          allowOutsideClick: () => !Swal.isLoading()
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire(
            'Experimento eliminado!',
            'Tu experimento ha sido eliminado',
            'success'
          ).then(function() {
              window.location = "create-experimentation"; // Reload page in order to show change in table.
          })
        }
      })
});

// set up the event listener for the edit button
$(".edit-button").on('click', function(){

  // pass the row context as parameter and select the row without highlighting it
  context = this.parentElement.parentElement.parentElement.parentElement;
  selectRowManual(context, false);

  // the edit button has been clicked, so set up the variable to true
  edit_clicked = true

});

function selectRowManual(context, highlight){

  // get the elements fo the selected row
  var array_td_element = $(context).children();

  // get the id number
  id_number = array_td_element[0].innerHTML.trim();

  //Remove class disabled in order to allow send load experiments
  $("#load-experiment").prop("disabled",false);

  // highlight the row if the user is selecting a row
  if (highlight == true){

    //Function changes color  rows select when you click above them in the table_experiments, so we will know that row we have  select.
    $(context).addClass('highlight').siblings().removeClass('highlight');
    edit = "";
  }

  // if it is the edit button, populate the edit form
  else{
    edit = "_edit_"+id_number;
  }

  // Fill field hidden that it will be send with the form load experiment
  $("#id_exp"+edit).val(array_td_element[0].innerHTML.trim());
  $("#date_create_exp"+edit).val(array_td_element[1].innerHTML.trim());
  $("#name_exp"+edit).val(array_td_element[2].innerHTML.trim());
  $("#select_bbdd"+edit).val(array_td_element[3].innerHTML.trim());
  $("#date_init"+edit).val(array_td_element[4].innerHTML.trim());
  $("#date_end"+edit).val(array_td_element[5].innerHTML.trim());
  $("#filter_apply"+edit).val(array_td_element[6].innerHTML.trim());

}