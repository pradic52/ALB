// Fonction pour récupérer le token CSRF depuis les cookies
function getCSRFToken() {
    let cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        let [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

// Afficher le formulaire de création de produit lorsque l'utilisateur clique sur le bouton
document.getElementById('show-form-btn').addEventListener('click', function() {
    document.getElementById('product-form-container').style.display = 'block';
});

// Gérer la soumission du formulaire avec AJAX
document.getElementById('product-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Empêcher le rechargement de la page

    let formData = new FormData(this);

    fetch(productCreateUrl, {
        method: "POST",
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCSRFToken() // Inclure le token CSRF dans l'en-tête
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data, 'je suis data');
        let url_delete;
        if (data.errors) {
            // Afficher les erreurs de validation si le formulaire est invalide
            document.getElementById('error-message').innerText = "Erreur : " + JSON.stringify(data.errors);
        } else {
            // Créer une nouvelle ligne pour le produit ajouté
            url_delete = productDeleteUrl(data.id);
            let newRow = `
                <tr>
                    <td>${data.id}</td>
                    <td class="bg-primary-subtle"><a href="#" style="text-decoration-line: none">${data.name} ${data.type}</a></td>
                    <td>${data.price}</td>
                    <td>${data.price_big_customer}</td>
                    <td><p class="d-flex justify-content-between">
                    <span>
                        ${data.alcoholic ? "Il contient de l'alcool" : "Il ne contient pas d'alcool"}
                        et
                        ${data.recycling ? "il est recyclable" : "il n'est pas recyclable"}
                    </span>
                        <button class="btn btn-danger justify-content-end" onclick="window.location.href='${url_delete}'">Supprimer</button>

                    </p></td>
                </tr>
            `;

            let tbody = document.querySelector("table tbody");

            // Ajouter temporairement la nouvelle ligne
            tbody.insertAdjacentHTML('beforeend', newRow);

            // Trier toutes les lignes après l'ajout
            let rows = Array.from(tbody.querySelectorAll("tr"));
            rows.sort((a, b) => {
                let nameA = a.querySelector("td:nth-child(2)").textContent.trim().toLowerCase();
                let nameB = b.querySelector("td:nth-child(2)").textContent.trim().toLowerCase();
                return nameA.localeCompare(nameB);
            });

            // Réinsérer les lignes triées dans le tableau
            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));

            // Réinitialiser le formulaire et masquer la zone de création
            document.getElementById('product-form').reset();
            document.getElementById('product-form-container').style.display = 'none';
            document.getElementById('error-message').innerText = "";
        }
    })
    .catch(error => console.error("Erreur :", error));
});
