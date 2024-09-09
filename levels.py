def levels(game, score):
    if score == 1:
        game.wall.columns = 1
    elif score == 2:
        game.wall.columns = 3
    elif score == 3:
        game.wall.columns = 6
    elif score == 4:
        game.wall.columns = 9
    elif score == 5:
        game.wall.columns = 9
        game.perpetio.height = 85
        game.perpetio.width = 45
        game.perpetio.pos = (675, 0)
    elif score == 6:
        game.perpetio.height = 100            
    elif score == 7:
        game.perpetio.width = 70
        game.perpetio.pos = (650, 0)
    elif score == 8:
        game.perpetio.width = 95
        game.perpetio.pos = (625, 0)
    elif score == 9:
        game.perpetio.width = 120
        game.perpetio.pos = (600, 0)
        game.mirror.pos = (400, 300)
        game.mirror.size = (170, 30)
    elif score == 10:
        game.perpetio.width = 170
        game.perpetio.pos = (550, 0)
    game.wall.build_wall()