"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import pandas as pd

KINDS = ['VAR', 'ARG', 'STATIC', 'FIELD']


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        # Your code goes here!
        self.static_table = pd.DataFrame({'Type': [], 'Kind': [], '#': []})
        self.local_table = pd.DataFrame({'Type': [], 'Kind': [], '#': []})
        # shira gelbstein has changed the code
        pass

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.local_table = pd.DataFrame({'Type': [], 'Kind': [], '#': []})

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """

        count = self.var_count(kind)
        if kind in ['local', 'argument']:
            self.local_table = self.local_table.append(
                pd.DataFrame({'Type': [type], 'Kind': [kind], '#': [count]}, index=[name]))
        else:
            self.static_table = self.static_table.append(
                pd.DataFrame({'Type': [type], 'Kind': [kind], '#': [count]}, index=[name]))

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind in ['local', 'argument']:
            return int((self.local_table['Kind'] == kind).sum())
        else:
            return int((self.static_table['Kind'] == kind).sum())

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.local_table.index:
            kind = self.local_table.loc[name, "Kind"]
        else:
            kind = self.static_table.loc[name, "Kind"]
        if kind == "field":
            return "this"
        else:
            return kind

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.local_table.index:
            type_x = self.local_table.loc[name, "Type"]
        else:
            type_x = self.static_table.loc[name, "Type"]
        return type_x

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.local_table.index:
            i = self.local_table.loc[name, "#"]
        else:
            i = self.static_table.loc[name, "#"]
        return int(i)

    def find_name (self, name):
        if name in self.local_table.index or name in self.static_table.index:
            return True
        else:
            return False

    def kind_count(self, kind):
        if kind in self.local_table['Kind'].values:
            return self.local_table['Kind'].value_counts()[kind]
        elif kind in self.static_table['Kind'].values:
            return self.static_table['Kind'].value_counts()[kind]
        return 0
