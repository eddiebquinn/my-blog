import os
import shutil
import yaml

class Signed_Post:

    def __init__(self, path:str):
        self.path = path
        self.content = self._read_contents()

    def _read_contents(self):
        with open(self.path, 'r') as file:
            contents = file.read()
        return contents
    
    def seperate_yaml(self, content:str) -> tuple:
        yaml_end_index = self.content.find("\n---\n", 1)
        if yaml_end_index != 1:
            yaml_end_index += len("\n---\n")
        
        yaml_content =  self.content[:yaml_end_index]
        content_after_yaml = self.content[yaml_end_index:]

        return (yaml_content, content_after_yaml)

    def modify_post(self, overwrite:bool = False):
        # Seperate out YAML
        seperated_content = self.seperate_yaml(self.content)

        # Change YAML outputs tag
        yaml_string = seperated_content[0]
        yaml_documents = yaml_string.split("---\n")
        yaml_data = yaml.safe_load(yaml_documents[1])
        yaml_data['outputs'] = 'standardFormat'
        modified_yaml_str = "---\n" + yaml.dump(yaml_data) + "---\n"

        # Strip out begining
        content_start_index = seperated_content[1].find("\n\n")
        if content_start_index != -1:
            stripped_content = seperated_content[1][content_start_index +2:]
        
        # strip out end
        sig_start_index = stripped_content.rfind("-----BEGIN PGP SIGNATURE-----")
        if sig_start_index != -1:
            stripped_content = stripped_content[:sig_start_index]
        
        # reassemble with yaml
        stripped_content = modified_yaml_str + stripped_content

        if overwrite:
            with open(self.path, 'w') as file:
                file.write(stripped_content)
                print(f"{self.path} overwritten")

        return stripped_content

class Directory_Strcture:

    def __init__(self, directory:str, whitelist:list):
        self.directory = directory
        self.sig_directory = whitelist[0]
        self.non_sig_files = self._build_list(whitelist)

    def _build_list(self, whitelist) -> dict:
        for root, dirs, files in os.walk(self.directory):
            for i in whitelist:
                if i in dirs:
                    dirs.remove(i)
                if i in files:
                    files.remove(i)
            return {"root": root, "dirs": dirs, "files": files}

    def purge_nonsig(self):
        for file_name in self.non_sig_files["files"]:
            file_path = os.path.join(self.non_sig_files["root"], file_name)
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        
        for dir_name in self.non_sig_files["dirs"]:
            dir_path = os.path.join(self.non_sig_files["root"], dir_name)
            shutil.rmtree(dir_path)
            print(f"Deleted: {dir_path}")
    
    def copy_files(self):
        sigs_folder = f"{self.directory}/{self.sig_directory}"
        for root, dirs, files in os.walk(sigs_folder):
            for file_name in files:
                src_path = os.path.join(root, file_name)
                dest_path = os.path.join(self.directory, os.path.relpath(src_path, sigs_folder))
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path)
                print(f"{src_path} -> {dest_path}")
    
    def bulk_modify_post(self):
        for file_name in self.non_sig_files["files"]:
            signed_post = Signed_Post(f'{self.directory}/{file_name}')
            signed_post.modify_post(overwrite=True)
        
        for dir_name in self.non_sig_files["dirs"]:
            for root, dirs, files in os.walk(f'{self.directory}/{dir_name}'):
                for file_name in files:
                    signed_post = Signed_Post(os.path.join(root, file_name))
                    signed_post.modify_post(overwrite=True)



def main(content_dir:str, sigs_dir:str):
    script_directory = os.path.dirname(__file__)
    parent_directory = os.path.abspath(os.path.join(script_directory, os.pardir))  # Navigate up one level
    content_directory = os.path.join(parent_directory, content_dir)
    directory_structure = Directory_Strcture(directory=content_directory, whitelist=[f"{sigs_dir}", ".git", ".gitignore"])
    directory_structure.purge_nonsig()
    directory_structure.copy_files()
    directory_structure.bulk_modify_post()

if __name__ == "__main__":
    # Define the relative paths to the content and sigs directories
    CONTENT_DIR = "content"
    SIGS_DIR = "sigs"

    # Call the main function with the relative paths
    main(content_dir=CONTENT_DIR, sigs_dir=SIGS_DIR)