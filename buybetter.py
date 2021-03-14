import streamlit as st
import pandas as pd 
import openfoodfacts

header = st.beta_container()
logo = st.beta_container()
preferences = st.beta_container()
input = st.beta_container()
suggestions = st.beta_container()

with header:
    st.title('Buy better - be better')  

with preferences:
    st.write('### You can enter or change your preferences on the left side.')
    organicpr = st.sidebar.selectbox('How important are organic labels to you?', options=['Very important', 'Important', 'Not important'], index=2)
    carbonpr = st.sidebar.selectbox('Do you prefer products with low carbon footprint?', options=['Yes', 'No'], index=1)
    fairpr = st.sidebar.selectbox('How important are fairtrade labels to you?', options=['Very important', 'Important', 'Not important'], index=2)
    animalpr = st.sidebar.selectbox('Do you prefer vegetarian or vegan products?', options=['No', 'Yes, vegetarian', 'Yes, vegan'], index=1)

with input:
    st.header('Please enter the barcode of your product:')
    barcode = st.text_input('Barcode')

    if barcode == "":
        st.write("Please enter your barcode")
    else:
        item = openfoodfacts.products.get_product(barcode)
        st.write('### Your product:')
        st.write("Name: " , item['product']['product_name'])
        #st.write("Categories: ", item['product']['categories'])
        st.write('Brand:', item['product']['brands'])

with suggestions:
    
    if barcode!="":
        st.header('Also consider these products:')
        item = openfoodfacts.products.get_product(barcode)
        categories=item['product']['categories']
        dfcategories = categories.split(",")
        firstCategorie = dfcategories[0]
        lastCategorie = dfcategories[-1]
        st.write("Kategorie: ", lastCategorie)

        otherProducts = openfoodfacts.products.advanced_search({
            "action" : "process",
            "tagtype_0" : "categories",
            "tag_contains_0" : "contains",
            "tag_0" : lastCategorie,
            "sort_by" : "unique_scans" ,
            "page_size" : "10"
        })

        #Attribut bbscore im Dictionary otherProducts unter Produkten für unseren Score anlegen und auf 0 setzen
        j=0
        for v in otherProducts['products']:
            otherProducts['products'][j]['bbscore'] = 0
            j=j+1

        #st.write(otherProducts['products'][0]['bbscore']) #zeigt den bbscore des ersten Produkts
        #st.write(otherProducts)
        i=0
        for u in otherProducts['products']:
            organic = False
            carbon = False
            fair = False
            vegetarian = False
            vegan = False
            lowprocessed = 50
            
            k=0
            for x in otherProducts['products'][i]['labels_tags']:           
                if otherProducts['products'][i]['labels_tags'][k] == 'en:organic':
                    organic = True
                elif otherProducts['products'][i]['labels_tags'][k] == 'en:carbon-footprint':
                    carbon = True
                elif otherProducts['products'][i]['labels_tags'][k] == 'en:fair-trade':
                    fair = True
                elif otherProducts['products'][i]['labels_tags'][k] == 'en:vegetarian':
                    vegetarian = True
                elif otherProducts['products'][i]['labels_tags'][k] == 'en:vegan':
                    vegan = True     
                k=k+1
            
            #Prüfung Bio
            if organicpr == 'Very important' and organic== True:
                otherProducts['products'][i]['bbscore'] = otherProducts['products'][i]['bbscore'] + 10
            elif organicpr == 'Important' and organic == True:
                otherProducts['products'][i]['bbscore'] = otherProducts['products'][i]['bbscore'] + 7.5
        
            #Prüfung carbon food print
            if carbonpr == 'Yes' and carbon == True:
                otherProducts['products'][i]['bbscore'] = otherProducts['products'][i]['bbscore'] + 10

            #Prüfung fairtrade
            if fairpr == 'Very important' and fair== True:
                otherProducts['products'][i]['bbscore'] = otherProducts['products'][i]['bbscore'] + 10
            elif fairpr == 'Important' and organic == True:
                otherProducts['products'][i]['bbscore'] = otherProducts['products'][i]['bbscore'] + 7.5
            
            #Prüfung vegetarisch/vegan
            if animalpr == 'Yes, vegetarian' and vegetarian== False:
                otherProducts['products'][i]['bbscore'] = otherProducts['products'][i]['bbscore'] - 100
            elif animalpr == 'Yes, vegan' and vegan == False:
                otherProducts['products'][i]['bbscore'] = otherProducts['products'][i]['bbscore'] - 100  

            i = i + 1        
            
        #Sortieren nach dem bbscore
        otherProducts['products'].sort(key=lambda x: x['bbscore'], reverse=True)
        #st.write(otherProducts)
        #if otherProducts['products'][0] 
        #st.write(otherProducts['products'][0])
        
        f=0
        for z in otherProducts['products'] :
            fsug = otherProducts['products'][f]
            st.write('### Suggestion ', f+1)
            st.write("Name: " , fsug['product_name'])
            #st.write("Categories: ", fsug['categories'])
            st.write('Brand:', fsug['brands'])
            st.write('Barcode:', fsug['code'])
            f=f+1
            if f == 5:
                break

st.write('##### Data Source: Open Food Facts (https://de.openfoodfacts.org/)')
st.write('##### This is a Techlabs-Project')