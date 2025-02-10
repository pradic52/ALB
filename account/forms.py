from django import forms



class LoginForm(forms.Form):
    username = forms.CharField(max_length=100,min_length=3,label="Nom d'utilisateur :", required=True)
    password = forms.CharField(label="Mot de passe :",widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('Veuillez entrer un nom d\'utilisateur valide')
        return username
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('Veuillez entrer un mot de passe valide')
        return password

    def clean(self):
        username = self.clean_username()
        password = self.clean_password()

        if not username and not password:
            raise forms.ValidationError("Tous les champs sont obligatoires")

        return self.cleaned_data

