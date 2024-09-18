document.addEventListener('alpine:init', () => {
    Alpine.data('imgPreview', () => ({
      imgsrc:null,
      previewFile() {
        let file = this.$refs.myFile.files[0];
        if(!file || file.type.indexOf('image/') === -1) return;
        this.imgsrc = null;
        let reader = new FileReader();
  
        reader.onload = e => {
          this.imgsrc = e.target.result;
        }
  
        reader.readAsDataURL(file);
      
      }
    }))
  });
  
  console.log('Js file')