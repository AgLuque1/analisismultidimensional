from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from .models import Experiment, Profile, DataBaseSystem
import json


class ProfileForm(ModelForm):
    first_name  = forms.CharField(
                        widget=forms.TextInput(
                            attrs={
                                'class':'form-control',
                                'placeholder':'Nombre de usuario'
                            }),
                        label="Nombre")
    
    last_name   = forms.CharField(widget=forms.TextInput(
                            attrs={
                                'class':'form-control',
                                'placeholder':'Apellidos'
                            }), label="Apellidos")

    image       = forms.ImageField(required=False, label="Foto de Perfil")
    
    email       = forms.EmailField(widget=forms.EmailInput(
                            attrs={
                                'class':'form-control',
                                'placeholder':'Email'
                            }),label="Email")
    
   
    address     = forms.CharField(widget=forms.TextInput(
                            attrs={
                                'class':'form-control',
                                'placeholder':'Dirección'
                            }), label="Direccion")

    education   = forms.CharField(widget=forms.TextInput(
                            attrs={
                                'class':'form-control',
                                'placeholder':'Organización'
                            }), label="Organización")
                            
    skill       = forms.CharField(widget=forms.Textarea(
                            attrs={
                                'class':'form-control',
                                'placeholder':'Habilidades',
                                'id':'inputSkill',
                            }),label="Habilidades")

    bio         = forms.CharField(widget=forms.Textarea(
                            attrs={
                                'class':'form-control',
                                'placeholder':'Bio',
                                'id':'inputBio',
                                
                            }), label="Bio")

    class Meta:
        model = Profile
        fields =('first_name', 'last_name',  'email', 'image', 'address', 'education', 'skill', 'bio' )

  #def __init__(self,*args,**kwargs):
        
  #      if 'all_bbdd' in kwargs:
  #          bbdd = kwargs.pop('all_bbdd')
  #          bbdd = json.loads(bbdd.text)   
# creating a form
class NewExperimentForm(ModelForm):
    
        name    = forms.CharField(widget=forms.TextInput(
                            attrs={
                            'class':'form-control',
                            'placeholder':'Inserte el título del Experimento',
                            'required':True,
                            }),
                            label="Titulo del Experimento",
                            error_messages={
                                'required':'Debes de introducir un titulo para la experimentación.',

                            })

        name_bbdd  = forms.ChoiceField(
                                        widget = forms.Select(
                                            attrs={
                                                'class':'form-control',
                                        }),
                                        label="Seleccione la Base de Datos",
                                        #choices=[ k for elem  in bbdd  for k,v in elem.items()],
                                        #choices=[("Prueba","Prueba"),("Prueba2","Prueba2")]
        )

        date_init    = forms.DateField(label="Fecha de inicio:",
                                        widget = forms.DateInput(
                                            format='%d/%m/%Y',
                                            attrs={
                                                'id':'datepicker_init',
                                                'autocomplete':'off',

                                        }),
                                        required=False,
                                        input_formats=["%d/%m/%Y"],
                                    )
        date_end     = forms.DateField(label="Fecha de fin:",
                                        widget = forms.DateInput(
                                            format='%d/%m/%Y',
                                            attrs={
                                                'id':'datepicker_end',
                                                'autocomplete':'off',
                                                'requiered':'False',
                                        }),
                                        required=False,
                                        input_formats=["%d/%m/%Y"],
                        )
        def __init__(self,*args,**kwargs):
            if 'all_bbdd' in kwargs:
                bbdd = kwargs.pop('all_bbdd')
                super(NewExperimentForm,self).__init__(*args, **kwargs )
                self.fields['name_bbdd'].choices=[ (k,v) for elem  in bbdd  for k,v in elem.items()]

        class Meta: 
            model = Experiment
            fields =('name', 'name_bbdd','date_init','date_end')
     
    
       
    
    
