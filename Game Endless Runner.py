from ursina import *
import random 
import os

app = Ursina()

window.size = (1280, 720) 
window.fullscreen=True

bg_speeds = [0.1, 0.2, 0.3, 0.4, 0.5]
bg_layers = [
    [Entity(model='quad', texture=f'Resource/plx-{i}.png', scale=(35, 20), z=6-i, x=35*j) for j in range(2)]
    for i in range(1, 6)
]

player = Animation('Resource/adven', scale=(4, 4), collider='box', x=-10, y=-6)
player.collider = BoxCollider(player, center=(0, -0.2, 0), size=(0.5, 0.6, 1))


player_roll_animation = Animation('Resource/roll', scale=(4, 4), collider='box', x=-10, y=-6 )
player_roll_animation.collider = BoxCollider(player_roll_animation, center=(0, 0.75, 0), size=(0.5, 1.5, 1))
player_roll_animation.enabled = False


roll_frames = [f'Resource/roll{i}' for i in range(1, 5)]

roll_frame_change_interval = 0.3
roll_frame_time = 0


ground_layers = [
    Entity(model='cube', texture='Resource/ground', color=color.green, collider='box', scale=(50, 3, 1), y=-10, x=50*i)
    for i in range(3)
]

fly = Entity(model='cube', collider='box', texture='Resource/monster1', scale=1.5, x=20, y=-10)


monster_frames = [f'Resource/monster{i}' for i in range(1, 4)]
current_monster_frame = 0
fly_frame_change_interval = 0.5
fly_frame_time = 0


flies = []


spike = Entity(model='cube', collider='box', texture='Resource/spikes_1', scale=1, x=20, y=-10)


spike_frames = ['Resource/spikes_1', 'Resource/spikes_2']
current_spike_frame = 0
spike_frame_change_interval = 0.5
spike_frame_time = 0


spikes = []


gravity = -30
jump_speed = 15
fall_speed_multiplier = 5  
is_jumping = False
velocity_y = 0


you_die_text = Text("You Die", origin=(0, 0), scale=3, color=color.red, enabled=False)


score = 0
score_text = Text(f'Score: {score}', position=(-0.85, 0.45), scale=2, color=color.white)
score_increment_interval = 0.1 
score_time = 0
score_speedup = 0.001  


best_score = score
best_score_text = Text(f'Best Score: {best_score}', position=(-0.85, 0.35), scale=2, color=color.yellow)


menu_background = Entity(model='quad', color=color.black, scale=(35, 20), z=5, visible=False)
start_button = Button(text='Start', scale=(0.2, 0.1), position=(0, 0.1), on_click=lambda: start_game(), visible=False)
quit_button = Button(text='Quit', scale=(0.2, 0.1), position=(0, -0.1), on_click=lambda: application.quit(), visible=False)

game_active = False

def show_menu(): 
    global game_active
    game_active = False
    menu_background.visible = True
    start_button.visible = True
    quit_button.visible = True

def hide_menu():
    global game_active
    game_active = True
    menu_background.visible = False
    start_button.visible = False
    quit_button.visible = False

def start_game():
    hide_menu()
    restart_game()


def save_best_score(score):
    with open('best_score.txt', 'w') as file:
        file.write(str(score))


def load_best_score():
    if os.path.exists('best_score.txt'):
        with open('best_score.txt', 'r') as file:
            return int(file.read())
    return 0


def new_fly():
    new_y = -4  
    new = duplicate(fly, y=new_y)
    flies.append(new)


def new_spike():
    new_y = -8 
    new = duplicate(spike, y=new_y)
    spikes.append(new)

def spawn_fly_random():
    invoke(new_fly, delay=random.uniform(2, 5))  
    invoke(spawn_fly_random, delay=random.uniform(2, 5))  

    

#├─ invoke(new_fly, delay=random.uniform(2, 5))
#│    └─ new_fly()  <-- Membuat musuh baru setelah jeda waktu acak
#└─ invoke(spawn_fly_random, delay=random.uniform(2, 5))
 #    └─ spawn_fly_random()  <-- Memanggil dirinya sendiri setelah jeda waktu acak, mengulang proses

 #Dengan cara ini, fungsi-fungsi ini menciptakan aliran konstan musuh dan rintangan yang muncul secara acak, yang sangat penting untuk menjaga dinamika dan tantangan dalam permainan.

def spawn_spike_random():
    invoke(new_spike, delay=random.uniform(2, 6))  
    invoke(spawn_spike_random, delay=random.uniform(3, 7))  

# Camera settings
camera.orthographic = True
camera.fov = 20

def restart_game():
    global is_jumping, velocity_y, current_roll_frame, score, score_time, score_increment_interval,best_score
    you_die_text.enabled = False
    player.rotation_z = 0
    velocity_y = 0
    current_roll_frame = 0
    best_score_text.text = f'Best Score: {best_score}'
    score = 0
    score_time = 0
    score_increment_interval = 0.1
    score_text.text = f'Score: {score}'
    for f in flies:
        destroy(f)
    flies.clear()
    for f in spikes:
        destroy(f)
    spikes.clear()


def update():
    global is_jumping, velocity_y, current_roll_frame, roll_frame_time, current_monster_frame, fly_frame_time, current_spike_frame, spike_frame_time, score, score_time, score_increment_interval, best_score

    if not game_active:
        return

    
    score_time += time.dt
    if score_time >= score_increment_interval:
        score_time = 0
        score += 1
        score_text.text = f'Score: {score}'
        score_increment_interval = max(0.05, score_increment_interval - score_speedup)  


    speed_multiplier = score / 50 
    for layer in bg_layers:
        for bg in layer:
            bg.x -= bg_speeds[bg_layers.index(layer)] * speed_multiplier * time.dt
            if bg.x <= -35:
                bg.x += 70


    for ground_layer in ground_layers:
        ground_layer.x -= 0.5 * speed_multiplier * time.dt
        if ground_layer.x <= -75:  #
            ground_layer.x += 150

    velocity_y += gravity * time.dt

    if is_jumping and held_keys['s']:
        velocity_y += gravity * (fall_speed_multiplier) * time.dt
        player.enabled = False
        player_roll_animation.enabled = True


        roll_frame_time += time.dt
        if roll_frame_time >= roll_frame_change_interval:
            roll_frame_time = 0
            current_roll_frame = (current_roll_frame + 1) % len(roll_frames)
            player_roll_animation.texture = roll_frames[current_roll_frame]
    else:
        player.enabled = True
        player_roll_animation.enabled = False

    player.y += velocity_y * time.dt
    player_roll_animation.y = player.y  
    player_roll_animation.x = player.x  

    for ground_layer in ground_layers:
        if player.intersects(ground_layer).hit:
            player.y = ground_layer.y + ground_layer.scale_y / 2 + player.scale_y / 2.1
            is_jumping = False
            velocity_y = 0

    player.x -= held_keys['a'] * 6 * time.dt
    player.x += held_keys['d'] * 6 * time.dt

    for fly in flies[:]:  
        fly.x -= 2 * speed_multiplier * time.dt
        fly_frame_time += time.dt
        if fly_frame_time >= fly_frame_change_interval:
            fly_frame_time = 0
            current_monster_frame = (current_monster_frame + 1) % len(monster_frames)
            fly.texture = monster_frames[current_monster_frame]
        if fly.x < -18: 
            flies.remove(fly)
            destroy(fly)
        touch = fly.intersects()
        if touch.hit:
            flies.remove(fly)
            destroy(fly)
            if touch.entity == player or touch.entity == player_roll_animation:
                you_die_text.enabled = True
                if score > best_score:
                    best_score = score
                    save_best_score(best_score)
                invoke(show_menu, delay=2)
            else:
                destroy(touch.entity)

    for spike in spikes[:]: 
        spike.x -= 2 * speed_multiplier * time.dt
        spike_frame_time += time.dt
        if spike_frame_time >= spike_frame_change_interval:
            spike_frame_time = 0
            current_spike_frame = (current_spike_frame + 1) % len(spike_frames)
            spike.texture = spike_frames[current_spike_frame]
        if spike.x < -18:  
            spikes.remove(spike)
            destroy(spike)
        touch = spike.intersects()
        if touch.hit:
            if spike in spikes:
                spikes.remove(spike)
            destroy(spike)
            if touch.entity == player or touch.entity == player_roll_animation:
                you_die_text.enabled = True
                if score > best_score:
                    best_score = score
                    save_best_score(best_score)
                invoke(show_menu, delay=2)
            else:
                destroy(touch.entity)


def input(key):
    global is_jumping, velocity_y

    if not game_active:
        return

    if key == 'space' and not is_jumping:
        velocity_y = jump_speed
        is_jumping = True

    if key == 'left mouse down':
        bullet = Entity(y=player.y, x=player.x + 1, model='cube', scale=0.2, texture='Resource/bullet-s', collider='cube')
        bullet.animate_x(30, duration=2, curve=curve.linear)
        


best_score = load_best_score()
best_score_text.text = f'Best Score: {best_score}'


spawn_fly_random()
spawn_spike_random()


show_menu()

app.run()

# Penjelasan variabel:

# 'app' adalah inisialisasi aplikasi Ursina.
# 'window.size' mengatur ukuran jendela aplikasi menjadi 1280x720 piksel.
# 'bg_speeds' adalah daftar yang menyimpan kecepatan untuk setiap lapisan latar belakang.
# 'bg_layers' adalah daftar yang menyimpan entitas untuk setiap lapisan latar belakang.
# 'player' adalah entitas pemain dengan animasi.
# 'player_roll_animation' adalah entitas animasi roll pemain.
# 'roll_frames' adalah daftar yang menyimpan frame animasi roll pemain.
# 'roll_frame_change_interval' adalah interval waktu untuk perubahan frame animasi roll.
# 'roll_frame_time' adalah variabel yang menyimpan waktu untuk perubahan frame animasi roll.
# 'ground_layers' adalah daftar yang menyimpan entitas untuk lapisan tanah.
# 'fly' adalah entitas musuh terbang.
# 'monster_frames' adalah daftar yang menyimpan frame animasi musuh terbang.
# 'current_monster_frame' adalah indeks frame animasi musuh terbang yang sedang aktif.
# 'fly_frame_change_interval' adalah interval waktu untuk perubahan frame animasi musuh terbang.
# 'fly_frame_time' adalah variabel yang menyimpan waktu untuk perubahan frame animasi musuh terbang.
# 'flies' adalah daftar untuk menyimpan musuh terbang yang aktif.
# 'spike' adalah entitas musuh spike.
# 'spike_frames' adalah daftar yang menyimpan frame animasi spike.
# 'current_spike_frame' adalah indeks frame animasi spike yang sedang aktif.
# 'spike_frame_change_interval' adalah interval waktu untuk perubahan frame animasi spike.
# 'spike_frame_time' adalah variabel yang menyimpan waktu untuk perubahan frame animasi spike.
# 'spikes' adalah daftar untuk menyimpan spike yang aktif.
# 'gravity' adalah variabel yang menyimpan nilai gravitasi.
# 'jump_speed' adalah variabel yang menyimpan kecepatan lompat pemain.
# 'fall_speed_multiplier' adalah pengali untuk mengatur kecepatan jatuh saat tombol 's' ditekan.
# 'is_jumping' adalah variabel boolean untuk mengecek apakah pemain sedang melompat.
# 'velocity_y' adalah variabel yang menyimpan kecepatan vertikal pemain.
# 'you_die_text' adalah teks yang muncul saat pemain mati.
# 'score' adalah variabel yang menyimpan skor pemain.
# 'score_text' adalah teks yang menampilkan skor pemain.
# 'score_increment_interval' adalah interval waktu untuk menambah skor.
# 'score_time' adalah variabel yang menyimpan waktu untuk penambahan skor.
# 'score_speedup' adalah percepatan interval waktu penambahan skor.
# 'best_score' adalah variabel yang menyimpan skor terbaik.
# 'best_score_text' adalah teks yang menampilkan skor terbaik.
# 'menu_background' adalah entitas latar belakang untuk menu awal.
# 'start_button' adalah tombol untuk memulai permainan.
# 'quit_button' adalah tombol untuk keluar dari aplikasi.
# 'game_active' adalah variabel boolean untuk mengecek apakah permainan sedang aktif.

# Fungsi 'show_menu' menampilkan menu awal.
# Fungsi 'hide_menu' menyembunyikan menu awal.
# Fungsi 'start_game' memulai permainan dengan memanggil 'hide_menu' dan 'restart_game'.
# Fungsi 'save_best_score' menyimpan skor terbaik ke file.
# Fungsi 'load_best_score' memuat skor terbaik dari file.
# Fungsi 'new_fly' membuat musuh terbang baru.
# Fungsi 'new_spike' membuat spike baru.
# Fungsi 'spawn_fly_random' mengatur spawn musuh terbang secara acak.
# Fungsi 'spawn_spike_random' mengatur spawn spike secara acak.
# Fungsi 'restart_game' mereset permainan.
# Fungsi 'update' dipanggil setiap frame untuk memperbarui logika permainan.