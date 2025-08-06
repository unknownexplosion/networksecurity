from setuptools import find_packages, setup
from typing import List 

def get_requirements() -> List[str]:
    """
    This Function will return list of requirements
    """
    requirement_lst: List[str] = []
    try:
        with open('requirements.txt', 'r') as file:
            # Read lines from the file
            lines = file.readlines()
            # Process each line
            for line in lines:
                requirement = line.strip()
                # Ignore empty lines and '-e.'
                if requirement and requirement != '-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("Requirement file not found")
    
    return requirement_lst

print(get_requirements())

setup(
    name="networksecurity",
    version="0.0.1",
    author="Anubhav Mukherjee",
    author_email="anubhavmukherjee28@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements()
)