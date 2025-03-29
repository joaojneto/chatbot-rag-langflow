from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message


class CustomComponent(Component):
    display_name = "String Splitter"
    description = "Splits an input string based on a separator."
    documentation: str = "https://docs.langflow.org/components-custom-components"
    icon = "code"
    name = "StringSplitter"

    # Definir entrada
    inputs = [
        MultilineInput(
            name="input_value",
            display_name="Input String",
            info="String to be split",
            value="Hello,World!",
            tool_mode=True,
        ),
        MessageTextInput(
            name="separator",
            display_name="Separator",
            info="Character to split the string",
            value=",",
        ),
    ]

    # Definir saída
    outputs = [
        Output(display_name="Message", name="output", method="build_output"),
    ]

    def build_output(self) -> Message:
        """Splits the input string based on the provided separator."""
        
        if self.input_value:
            input_value = self.input_value 
        else:
            input_value = ""  # Garantir que a string não seja None
        
        if self.separator:
            separator = self.separator  # Definir separador padrão
        else:
            separador = ","

        try:
            input_value = input_value.split(separator)  # Realiza o split
            input_value = input_value[1]
        except:
            input_value = input_value[0]

        #formatted_output = "\n".join(split_result)  # Formata como string única

        print(input_value)
        return input_value
