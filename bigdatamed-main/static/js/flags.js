var language = 'es';
    const flagsElement = document.getElementById("flags");
    const inputsToChange = document.querySelectorAll("input[data-placeholder]");
    const textsToChange = document.querySelectorAll("[data-section");

    const changeLanguage = async language=>{
        const requestJson = await fetch(`../static/languages/${language}.json`);
        const texts = await requestJson.json();

        for(const textToChange of textsToChange){
            
            const section = textToChange.dataset.section;
           
            const value = textToChange.dataset.value;
          
            textToChange.innerHTML = texts[section][value];
        }

        inputsToChange.forEach((inputToChange) => {
            
            const placeholderKey = inputToChange.dataset.placeholder;
            
            const translatedPlaceholder = texts.placeholders[placeholderKey];
            // Actualiza el placeholder del input
            
            inputToChange.placeholder = translatedPlaceholder;
          });

         
    }

   

    flagsElement.addEventListener("click", (e) => {
        language = e.target.parentElement.dataset.value;
        console.log(e.target.parentElement.dataset.value);
        
        changeLanguage(e.target.parentElement.dataset.language);
    });



