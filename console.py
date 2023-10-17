#!/usr/bin/python3
""" command line interpreter """

import cmd
from models.base_model import BaseModel
from models import storage
import json
import re

"""console application"""


class HBNBCommand(cmd.Cmd):
    """command interpreter """
    prompt = "(hbnb) "

    def precmd(self, line):
        """Intercepts commands to test for class.syntax()"""
        match = re.search(r"^(\w*)\.(\w+)(?:\(([^)]*)\))$", line)
        regx_match2 = r"^(\w+)\.(\w+)\(([^,]+),\s*([^,]+),\s*([^)]+)\)$"
        match2 = re.search(f"{regx_match2}", line)
        words = line.split(" ")
        number_of_arguements = len(words)
        """
            since both class_name.all() and
            <class name>.update(<id>, <dictionary representation>)
            will both match the two regex we use number of args
            to differentiate them
        """
        if match and number_of_arguements < 3:
            classname = match.group(1)
            method = match.group(2)
            _id = match.group(3)[1:-1]
            if not _id:
                if classname in storage.classes():
                    line = f"{method} {classname}"
                    return cmd.Cmd.precmd(self, line)
            else:
                key = "{}.{}".format(classname, _id)
                if key in storage.all():
                    line = "{} {} {}".format(method, classname, _id)
                    return cmd.Cmd.precmd(self, line)
                elif key not in storage.all():
                    line = "{} {} {}".format(method, classname, _id)
                    return cmd.Cmd.precmd(self, line)
        elif match2 and number_of_arguements > 2:
            classname = match2.group(1)
            method = match2.group(2)
            _id = match2.group(3)[1:-1]
            attribute_name = match2.group(4)[1:-1]
            att_val = match2.group(5)
            if att_val.startswith(("'", '"')) and att_val.endswith(("'", '"')):
                att_val = att_val[1:-1]
            key = "{}.{}".format(classname, _id)
            if key in storage.all():
                line = "{} {} {} {} {}".format(
                        method, classname,
                        _id, attribute_name,
                        att_val)
                return cmd.Cmd.precmd(self, line)
        else:
            return cmd.Cmd.precmd(self, line)

    def do_create(self, line):
        """
            Creates a new instance of BaseModel,
            saves it (to the JSON file) and prints the id
        """
        if not line or line == "":
            print("** class name missing **")
        elif line not in storage.classes():
            print("** class doesn't exist **")
        else:
            instance = storage.classes()[line]()
            instance.save()
            print(instance.id)

    def do_show(self, line):
        """
            Prints the string representation of an instance
            based on the class name and id.
            Ex: $ show BaseModel 1234-1234-1234.
        """
        if not line or line == "":
            print("** class name missing **")
        else:
            word = line.split(" ")
            if word[0] in storage.classes():
                if len(word) < 2:
                    print("** instance id missing **")
                else:
                    key = "{}.{}".format(word[0], word[1])
                    if key not in storage.all():
                        print("** no instance found **")
                    elif key in storage.all():
                        print(storage.all()[key])
            else:
                print("** class doesn't exist **")

    def do_destroy(self, line):
        """
            Deletes an instance based on the class name and id
            Ex: $ destroy BaseModel 1234-1234-1234.
        """
        if not line or line == "":
            print("** class name missing **")
        else:
            word = line.split(" ")
            if word[0] in storage.classes():
                if len(word) < 2:
                    print("** instance id missing **")
                else:
                    key = "{}.{}".format(word[0], word[1])
                    if key not in storage.all():
                        print("** no instance found **")
                    elif key in storage.all():
                        del storage.all()[key]
                        new = storage.all()
                        storage.save()
            else:
                print("** class doesn't exist **")

    def do_update(self, line):
        """Updates an instance by adding or updating attribute.
        """
        if line == "" or line is None:
            print("** class name missing **")
            return

        rex = r'^(\S+)(?:\s(\S+)(?:\s(\S+)(?:\s((?:"[^"]*")|(?:(\S)+)))?)?)?'
        match = re.search(rex, line)
        classname = match.group(1)
        uid = match.group(2)
        attribute = match.group(3)
        value = match.group(4)
        if not match:
            print("** class name missing **")
        elif classname not in storage.classes():
            print("** class doesn't exist **")
        elif uid is None:
            print("** instance id missing **")
        else:
            key = "{}.{}".format(classname, uid)
            if key not in storage.all():
                print("** no instance found **")
            elif not attribute:
                print("** attribute name missing **")
            elif not value:
                print("** value missing **")
            else:
                cast = None
                if not re.search('^".*"$', value):
                    if '.' in value:
                        cast = float
                    else:
                        cast = int
                else:
                    value = value.replace('"', '')
                attributes = storage.attributes()[classname]
                if attribute in attributes:
                    value = attributes[attribute](value)
                elif cast:
                    try:
                        value = cast(value)
                    except ValueError:
                        pass
                setattr(storage.all()[key], attribute, value)
                storage.all()[key].save()

    def update_dict(self, classname, uid, s_dict):
        """Helper method for update() with a dictionary."""
        s = s_dict.replace("'", '"')
        d = json.loads(s)
        if not classname:
            print("** class name missing **")
        elif classname not in storage.classes():
            print("** class doesn't exist **")
        elif uid is None:
            print("** instance id missing **")
        else:
            key = "{}.{}".format(classname, uid)
            if key not in storage.all():
                print("** no instance found **")
            else:
                attributes = storage.attributes()[classname]
                for attribute, value in d.items():
                    if attribute in attributes:
                        value = attributes[attribute](value)
                    setattr(storage.all()[key], attribute, value)
                storage.all()[key].save()

    def do_all(self, line):
        """Prints all string representation of all instances.
        """
        if line != "":
            words = line.split(' ')
            if words[0] not in storage.classes():
                print("** class doesn't exist **")
            else:
                nl = [str(obj) for key, obj in storage.all().items()
                      if type(obj).__name__ == words[0]]
                print(nl)
        else:
            new_list = [str(obj) for key, obj in storage.all().items()]
            print(new_list)

    def do_count(self, line):
        """Count current number of class instances"""
        count = 0
        for key, value in storage._FileStorage__objects.items():
            words = key.split(".")
            if line == words[0]:
                count += 1
        print(count)

    def do_quit(self, line):
        """commnad for quit"""
        return True

    def do_EOF(self, line):
        """enable contro d"""
        return True

    def emptyline(self):
        """Do nothing for empty line"""
        pass


if __name__ == '__main__':
    HBNBCommand().cmdloop()
