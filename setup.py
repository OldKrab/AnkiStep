from setuptools import find_packages, setup


setup(
    name='ankistep',
    version='0.0.1',
    description="An application for quickly exporting solved quizzes from a course on Stepik to Anki.",
    url="https://github.com/OldKrab/AnkiStep",
    install_requires=[
        'click',
        'requests',
        'sympy', 
        'joblib',
        'appdirs'
    ],
    packages=find_packages(),
        entry_points = {
        'console_scripts': ['ankistep=ui.console_ui:cli'],
    }
)
