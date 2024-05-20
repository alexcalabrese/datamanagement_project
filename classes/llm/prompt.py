class Prompt:
    """
    A class used to represent a Prompt

    Attributes
    ----------
    boilerplate : dict
        a dictionary representing the boilerplate for the prompt

    Methods
    -------
    __init__(self, content: str)
        Initializes the Prompt object with the given content.
    """

    def __init__(self, content: str) -> None:
        """
        Parameters
        ----------
        content : str
            The content of the prompt
        """
        self.content = content

        # if self.boilerplate is None:
        self.boilerplate = {
            "contents": [{"parts": [{"text": content}]}],
            "generationConfig": {"temperature": 0},
        }

    def get_content(self) -> str:
        """
        Returns the content of the prompt.

        Returns
        -------
        str
            The content of the prompt
        """
        return self.content

    def get_prompt(self) -> str:
        """
        Returns the content of the prompt.

        Returns
        -------
        str
            The content of the prompt
        """
        if self.boilerplate is None:
            return None
        if self.content is None:
            raise ValueError("Prompt content is None")

        return self.boilerplate
