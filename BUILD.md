 # Vivarium Sim Build Instructions

 ## Building the Project

 1. Open the root directory of the project (`src/`) in your terminal.
 2. Run the following command:
    ```bash
    ppython setup.py build_apps
    ```
 3. The project will be built for Linux, Mac, and Windows. The output will be located in a new directory called `build`.

 ---

 ## Common Debugging Tips

 - **Ensure Panda3D is Installed**  
   Verify that Panda3D is correctly installed in your environment. You can check this by running:
   ```bash
   ppython -m pip show panda3d
   ```
   If it’s not installed, add it using:
   ```bash
   ppython -m pip install panda3d
   ```

 - **Check Your Python Version**  
   The project is designed to run with the version of Python bundled with Panda3D (`ppython`). Ensure you are using `ppython` for all commands to avoid conflicts with your system's default Python installation.

 - **Missing Dependencies**  
   If the build process fails due to missing dependencies, install them using:
   ```bash
   ppython -m pip install -r requirements.txt
   ```

 - **Verbose Output**  
   For more detailed output during the build process, use the `--verbose` flag:
   ```bash
   ppython setup.py build_apps --verbose
   ```

 - **Clean Build**  
   If you encounter persistent issues, perform a clean build by deleting the `build/` directory and re-running the build command.

 ---

 ## Documentation Notes

 This project uses **pydoctor** for generating developer documentation. However, **do not include pydoctor in `requirements.txt`**, as it will cause the build process to fail. You can install pydoctor manually if needed for documentation generation:
 ```bash
 ppython -m pip install pydoctor
 ```

 To generate documentation:
 1. Navigate to the root directory of the project.
 2. Run the following command:
    ```bash
    ppython -m pydoctor --make-html --project-name VivariumSim --html-output docs
    ```
 3. The generated documentation will be located in the `docs/` directory.

 ---

 ## Additional Resources

 - [Panda3D Documentation](https://docs.panda3d.org/)