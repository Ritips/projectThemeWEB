from data import db_session


def main():
    db_session.global_init('db/Supercell_is_piece_of_sheet.sqlite')


if __name__ == '__main__':
    main()
