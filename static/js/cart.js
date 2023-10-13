

var updateBtns = document.getElementsByClassName('update-cart')


for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function(){
        var item_id = this.dataset.item
        var action = this.dataset.action
        if (this.dataset.description == undefined) {
            var description = ""
        }
        description = this.dataset.description
        

        console.log('USER:', user)
        if (user == 'AnonymousUser'){
            addCookieItem(null, action, description, false, item_id)
        }else{
            updateUserOrder(item_id, action, description)
        }
    })
}

    

function addCookieItem(productId, action, description, addFromCart=false, item_id = -1){
    console.log('User is not authenticated')
    // console.log(productId, action, description)

    cartLength = Object.keys(cart).length
    let exsit = false
    // Add the item to the cart in store page
    // If the item already exists in the cart, update the quantity
    if (addFromCart == true) {
        for (i = 0; i < cartLength; i++) {
            if (cart[i]['description'] == description && cart[i]['productId'] == productId) {
                cart[i]['quantity'] += 1
                exsit = true
            }
        }
        if (exsit == false) {
            cart[cartLength] = {'quantity':1, 'description':description, 'productId':productId}
        }
        document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    
    } else {
        // Update the cart in the cart page
        if (action == 'add') {
            cart[item_id]['quantity'] += 1
        }
        updateCartDisplay(item_id, action)
    }
    

}

function updateUserOrder(productId, action, description){
    console.log('User is authenticated, sending data...')
    var url = '/update_item/'
    
    fetch(url, {
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId': productId, 'action': action, 'description': description})
    })

    .then((response) =>{
        return response.json()
    })

    .then((data) =>{
        console.log('data:', data)
        location.reload()
    })
}


function updateCartDisplay(item_id, action) {

    const cartItemElement = document.querySelector('#cart-row-' + item_id); // Get the cart item element
    const itemTotalElement = cartItemElement.querySelector('#itemTotal'); // Get the item total element
    const quantityElement = cartItemElement.querySelector('.quantity'); // Get the quantity element
    let price = itemTotalElement.textContent.split("$")[1] / quantityElement.textContent 
    const grandItemsElement = document.querySelector('#grandItems');
    let grandItems = grandItemsElement.textContent
    const grandTotalElement = document.querySelector('#grandTotal');
    let grandTotal = grandTotalElement.textContent.split("$")[1]
    // <p id="cart-total">{{cartItems}}</p>
    const cartTotalElement = document.querySelector('#cart-total');
    if (action == 'remove'){
        cart[item_id]['quantity'] -= 1
        
        if (cart[item_id]['quantity'] <= 0){
            
            delete cart[item_id]
            cartItemElement.remove()
        }
    }

    if (cart[item_id] != undefined){
        // Update the quantity and total based on the cart data
        quantityElement.textContent = cart[item_id]['quantity'];
        itemTotalElement.textContent = "$" + (cart[item_id]['quantity'] * price).toFixed(2);
    }
    // <table class="table">
    //     <tr>
    //     <th><h5>Items: <Strong id="grandItems">{{order.get_cart_items}}</Strong></h5></th>
    //     <th><h5>Total: <Strong id="grandTotal">${{order.get_cart_total|floatformat:2}}</Strong></h5></th>
    //     <th>
    //         <a style="float:right; margin:5px" class="btn btn-success" id="checkout" href="{% url 'checkout' %}">Checkout</a>
    //     </th>
    // </tr>
    // </table>
    // Update the grandItems

    if (action == 'add'){
        grandItems = parseInt(grandItems) + 1
        grandTotal = parseFloat(grandTotal) + parseFloat(price)
    } else {
        grandItems = parseInt(grandItems) - 1
        grandTotal = parseFloat(grandTotal) - parseFloat(price)
    }

    if (grandItems <= 0){
        grandItems = 0
        grandTotal = 0
    }

    grandItemsElement.textContent = grandItems
    grandTotalElement.textContent = "$" + grandTotal.toFixed(2)
    cartTotalElement.textContent = grandItems

    console.log('Cart:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
    


}


// Call the updateCartDisplay function when the page loads to initialize the cart display
// You can loop through the cart data and update the display for each item
// Example:
// for (const productId in cart) {
//     updateCartDisplay(productId);
// }