import subprocess
def test_bake_project(cookies):
    result = cookies.bake(extra_context={"project_name": "Hello World"})

    assert result.exit_code == 0
    assert result.exception is None

    assert result.project_path.name == "hello_world"
    assert result.project_path.is_dir()

def test_setup_conda(cookies):
    result = cookies.bake(extra_context={"project_name": "Hello World", "venv_tool": "conda"})

    assert result.exit_code == 0
    assert result.exception is None

    assert (result.project_path / "setup_env.sh").exists()
    assert (result.project_path / "setup_env.sh").is_file()
    completed = subprocess.run(["bash", "setup_env.sh"], shell=False, capture_output=True, check=True)
    print("Done")
