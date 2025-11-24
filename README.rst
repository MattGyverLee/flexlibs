flexlibs
========

flexlibs is a library for accessing FieldWorks Language Explorer 
(FLEx) [1]_ projects.

flexlibs handles the necessary initialisation of the FLEx engine, and 
provides a class (FLExProject) for opening a FLEx project and working 
with its contents.

For the GUI application that runs Python scripts/plugins
on FLEx databases see FLExTools [2]_, which is built on flexlibs.


Requirements
------------

Python 3.8 - 3.13.

Python for .NET [3]_ version 3.0.3+.

FieldWorks Language Explorer 9.0.17 - 9.3.1.


32-bit vs 64-bit
^^^^^^^^^^^^^^^^
The Python architecture must match that of FieldWorks. I.e. Install 
32-bit Python for 32-bit Fieldworks, and 64-bit Python for 64-bit 
Fieldworks.

Installation
------------
Run:
``pip install flexlibs``

Usage
-----

Basic usage:

.. code-block:: python


  import flexlibs
  flexlibs.FLExInitialize()
  p = flexlibs.FLExProject()
  p.OpenProject('parser-experiments')
  p.GetPartsOfSpeech()
  # ['Adverb', 'Noun', 'Pro-form', 'Pronoun', 'Verb', 'Copulative verb', 'Ditransitive verb', 'Intransitive verb', 'Transitive verb', 'Coordinating connective']

  # The API documentation is an HTML file
  os.startfile(flexlibs.APIHelpFile)
  ...
  p.CloseProject()
  flexlibs.FLExCleanup()


Version 2.0+ Operations Classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Version 2.0 introduces comprehensive Operations classes providing CRUD
(Create, Read, Update, Delete) methods for all major FLEx data types.
These are organized into topic areas matching FLEx's structure:

- **Grammar**: Parts of Speech, Phonemes, Grammatical Categories, Morphology
- **Lexicon**: Entries, Senses, Examples, Pronunciations, Variants, Etymology
- **Texts & Words**: Texts, Wordforms, Analyses, Paragraphs, Segments
- **Notebook**: Notes, People, Locations, Anthropology data
- **Lists**: Publications, Agents, Overlays, Possibility Lists
- **System**: Writing Systems, Custom Fields, Project Settings

Example usage:

.. code-block:: python

  import flexlibs
  flexlibs.FLExInitialize()

  project = flexlibs.FLExProject()
  project.OpenProject('MyProject', writeEnabled=True)

  # Create a new lexical entry
  entry = project.LexEntry.Create("run", "stem")

  # Add a sense with gloss
  sense = project.LexEntry.AddSense(entry, "to move rapidly on foot")
  project.Senses.SetGloss(sense, "run", "en")

  # Set part of speech
  verb = project.POS.Find("Verb")
  project.Senses.SetPOS(sense, verb)

  # Add an example sentence
  example = project.Examples.Create(sense,
      "The dog runs in the park.", "en")

  project.CloseProject()
  flexlibs.FLExCleanup()

All v1.x API methods remain available for backward compatibility.

--------------

.. [1] https://software.sil.org/fieldworks/
.. [2] https://github.com/cdfarrow/flextools/wiki/
.. [3] https://github.com/pythonnet/pythonnet/wiki
