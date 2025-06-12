# code from main.py here

kc = KahootCreator()
mo = MultipleOption("Which one of this has a len() of 2", [0, 1, 2], "ex", "aa", "xs", "f")
kc.login("your_user", "password")
kc.create_question(mo)
kc.delete_question(0)
kc.save("my python created kahoot!")
