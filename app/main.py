from views.menu import Menu


def main():
    ''' Application initializer. '''
    menu: Menu = Menu()
    menu.render()


if __name__ == '__main__':
    main()
