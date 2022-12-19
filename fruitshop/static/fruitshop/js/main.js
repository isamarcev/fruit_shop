
let UpMoney = document.getElementById('up_money')
UpMoney.addEventListener('click', AccountMoney)
let DownMoney = document.getElementById('down_money')
DownMoney.addEventListener('click', AccountMoney, 'down')


function AccountMoney(operation) {
    alert(operation)
    let balance_count = document.getElementById('balance_input')
    // $.ajax(
    //
    // )
    alert(balance_count)
}

function DownAccountMoney() {
    let balance_count = document.getElementById('balance_input')
    console.log(balance_count.value)
    console.log("DOWN")
}