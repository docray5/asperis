import pygame

import core
from commands import ChangeColorToCmd
from ecs.components import TransformComp, RenderableComp, TileComp, RectToDrawComp, PlayerComp, PhysicsComp, EnemyComp, \
    EnemyType, HealthComp, AnimatedSpriteComp, ParticleComp, CircleToDrawComp, BossComp, AnimatedCharacterComp, \
    AnimationType, ClickableComp, LabelComp, TextureToDrawComp


def create_tile(entity_manager, x, y, width, height):
    tile_entity_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
    # physics_cmp = PhysicsComp()
    render_cmp = RenderableComp(pygame.Color(200, 200, 200))
    entity_manager.add_components(
        tile_entity_id,
        transform_cmp,
        render_cmp,
        TileComp(),
        RectToDrawComp())

    return tile_entity_id

def create_player(entity_manager, x, y, width, height):
    player_entity_id = entity_manager.create_entity()
    player_comp = PlayerComp()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
    render_cmp = RenderableComp(pygame.color.Color(255, 255, 255))
    physics_cmp = PhysicsComp()
    entity_manager.add_components(
        player_entity_id,
        player_comp,
        transform_cmp,
        render_cmp,
        physics_cmp,
        HealthComp(),
        RectToDrawComp())

    return player_entity_id

def create_enemy(entity_manager, x, y, width, height, max_speed=100, enemy_type=EnemyType.FOLLOWING):
    enemy_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
    render_cmp = RenderableComp(pygame.color.Color(255, 30, 30))
    physics_cmp = PhysicsComp()
    enemy_cmp = EnemyComp(enemy_type=enemy_type, max_speed=max_speed)
    entity_manager.add_components(
        enemy_id, transform_cmp, render_cmp, physics_cmp, enemy_cmp, HealthComp(), RectToDrawComp()
    )

    return enemy_id

def create_darker_overlay(entity_manager):
    entity_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(0, 0), core.VIEWPORT_WIDTH, core.VIEWPORT_HEIGHT)
    render_cmp = RenderableComp(pygame.color.Color(255, 255, 255), affected_by_camera=False)

    entity_manager.add_components(
        entity_id, transform_cmp, render_cmp, TextureToDrawComp(core.asset_manager.get("overlay.png"))
    )

    return entity_id

def create_button(entity_manager, x, y, width, height, text, on_click_cmd):
    x -= width / 2
    y -= height / 2

    entity_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), width, height)
    render_cmp = RenderableComp(pygame.color.Color(core.BUTTON_COLOR), affected_by_camera=False)
    clickable_cmp = ClickableComp(on_click_cmd, ChangeColorToCmd(render_cmp, pygame.Color(core.BUTTON_ON_HOVER_COLOR)), ChangeColorToCmd(render_cmp, pygame.Color(core.BUTTON_COLOR)))

    label_cmp = LabelComp(text, core.BUTTON_FONT_COLOR)
    label_cmp.font = pygame.font.SysFont(core.FONT_FAMILY, label_cmp.font_size)
    label_cmp.text_surface = label_cmp.font.render(label_cmp.text, True, label_cmp.color)

    entity_manager.add_components(
        entity_id, transform_cmp, render_cmp, clickable_cmp, RectToDrawComp(), label_cmp
    )

    return entity_id

def create_label(entity_manager, x, y, font_size, color: pygame.Color, text):

    entity_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), 0, 0)
    render_cmp = RenderableComp(color, affected_by_camera=False)

    label_cmp = LabelComp(text, color)
    label_cmp.font_size = font_size
    label_cmp.font = pygame.font.SysFont(core.FONT_FAMILY, label_cmp.font_size)
    label_cmp.text_surface = label_cmp.font.render(label_cmp.text, True, label_cmp.color)

    entity_manager.add_components(
        entity_id, transform_cmp, render_cmp, label_cmp
    )

    return entity_id

def create_animated_slash_particle(entity_manager, x, y, flip_x, flip_y, rotation):
    particle_id = entity_manager.create_entity()
    img1 = core.asset_manager.get("p_slash_frame1.png")
    img2 = core.asset_manager.get("p_slash_frame2.png")
    img3 = core.asset_manager.get("p_slash_frame3.png")
    img4 = core.asset_manager.get("p_slash_frame4.png")
    entity_manager.add_components(
        particle_id,
        TransformComp(pygame.math.Vector2(x, y - img1.get_size()[1]/2), img1.get_size()[0], img1.get_size()[0], rotation=rotation),
        RenderableComp(color=pygame.color.Color(255, 255, 255), flip_x=flip_x, flip_y=flip_y),
        AnimatedSpriteComp(frames=[img1, img2, img3, img4], animation_speed=0.05, one_shot=True)
    )

# def create_animated_slash_particle2(entity_manager, x, y, flip_x, scale):
#     particle_id = entity_manager.create_entity()
#     img1 = core.asset_manager.get("b_slash_frame1.png")
#     img2 = core.asset_manager.get("b_slash_frame2.png")
#     img3 = core.asset_manager.get("b_slash_frame3.png")
#     img4 = core.asset_manager.get("b_slash_frame4.png")
#     img5 = core.asset_manager.get("b_slash_frame5.png")
#     img6 = core.asset_manager.get("b_slash_frame6.png")
#     img7 = core.asset_manager.get("b_slash_frame7.png")
#     img8 = core.asset_manager.get("b_slash_frame8.png")
#     img9 = core.asset_manager.get("b_slash_frame9.png")
#     entity_manager.add_components(
#         particle_id,
#         TransformComp(pygame.math.Vector2(x, y - img1.get_size()[1] / 2), img1.get_size()[0], img1.get_size()[0],
#                       rotation=0, scale=scale),
#         RenderableComp(color=pygame.color.Color(255, 255, 255), flip_x=flip_x, flip_y=True),
#         AnimatedSpriteComp(frames=[img1, img2, img3, img4, img5, img6, img7, img8, img9], animation_speed=0.025, one_shot=True)
#     )

def create_circle_particle(entity_manager, x, y, radius: int, color: pygame.Color, angle_direction, speed, life_duration, time_to_change_opacity, affected_by_camera=True):
    particle_id = entity_manager.create_entity()
    circle_to_draw_cmp = CircleToDrawComp(pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA))
    entity_manager.add_components(
        particle_id,
        TransformComp(pygame.math.Vector2(x, y), radius, radius),
        ParticleComp(life_duration=life_duration, direction=angle_direction, speed=speed, time_to_change_opacity=time_to_change_opacity),
        circle_to_draw_cmp,
        RenderableComp(color, affected_by_camera=affected_by_camera)
    )

    prep_circle_surf(circle_to_draw_cmp.surface, color, radius)

# TODO this one could be poolable
def prep_circle_surf(surface: pygame.Surface, color: pygame.Color, radius: int):
    pygame.draw.circle(surface, color, (radius, radius), radius)

def create_boss(entity_manager, x, y):
    enemy_id = entity_manager.create_entity()
    transform_cmp = TransformComp(pygame.math.Vector2(x, y), core.BOSS_SIZE[0], core.BOSS_SIZE[1], scale=4)
    render_cmp = RenderableComp(pygame.color.Color(200, 20, 20))
    physics_cmp = PhysicsComp(knockback_resistance=0.15)
    enemy_cmp = EnemyComp(enemy_type=EnemyType.BOSS, max_speed=110, damage=2)

    base_animation_size = (core.asset_manager.get("boss_walk0.png").get_size()[0], core.asset_manager.get("boss_walk0.png").get_size()[1])
    print(base_animation_size)

    idle_frames = [
        core.asset_manager.get("boss_idle0.png"),
        core.asset_manager.get("boss_idle1.png"),
        core.asset_manager.get("boss_idle2.png"),
        core.asset_manager.get("boss_idle3.png"),
        core.asset_manager.get("boss_idle4.png"),
        core.asset_manager.get("boss_idle5.png"),
        core.asset_manager.get("boss_idle6.png"),
        core.asset_manager.get("boss_idle7.png"),
        core.asset_manager.get("boss_idle8.png"),
        core.asset_manager.get("boss_idle9.png"),
        core.asset_manager.get("boss_idle10.png")
    ]
    idle_anim_frames_obj = AnimatedSpriteComp(idle_frames, offset_x=abs(base_animation_size[0]-idle_frames[0].get_size()[0]), offset_y=0)

    moving_frames = [
        core.asset_manager.get("boss_walk0.png"),
        core.asset_manager.get("boss_walk1.png"),
        core.asset_manager.get("boss_walk2.png"),
        core.asset_manager.get("boss_walk3.png"),
        core.asset_manager.get("boss_walk4.png"),
        core.asset_manager.get("boss_walk5.png"),
        core.asset_manager.get("boss_walk6.png"),
        core.asset_manager.get("boss_walk7.png"),
        core.asset_manager.get("boss_walk8.png"),
        core.asset_manager.get("boss_walk9.png"),
        core.asset_manager.get("boss_walk10.png"),
        core.asset_manager.get("boss_walk11.png"),
        core.asset_manager.get("boss_walk12.png")
    ]
    moving_anim_frames_obj = AnimatedSpriteComp(moving_frames, offset_x=0, offset_y=0)

    hit_frames = [
        core.asset_manager.get("boss_hit0.png"),
        core.asset_manager.get("boss_hit1.png"),
        core.asset_manager.get("boss_hit2.png"),
        core.asset_manager.get("boss_hit3.png"),
        core.asset_manager.get("boss_hit4.png"),
        core.asset_manager.get("boss_hit5.png"),
        core.asset_manager.get("boss_hit6.png"),
        core.asset_manager.get("boss_hit7.png")
    ]
    hit_anim_frames_obj = AnimatedSpriteComp(hit_frames, one_shot=True, offset_x=abs(base_animation_size[0]-hit_frames[0].get_size()[0])-4, offset_y=0)

    attack_frames = [
        core.asset_manager.get("boss_attack0.png"),
        core.asset_manager.get("boss_attack1.png"),
        core.asset_manager.get("boss_attack2.png"),
        core.asset_manager.get("boss_attack3.png"),
        core.asset_manager.get("boss_attack4.png"),
        core.asset_manager.get("boss_attack5.png"),
        core.asset_manager.get("boss_attack6.png"),
        core.asset_manager.get("boss_attack7.png"),
        core.asset_manager.get("boss_attack8.png"),
        core.asset_manager.get("boss_attack9.png"),
        core.asset_manager.get("boss_attack10.png"),
        core.asset_manager.get("boss_attack11.png"),
        core.asset_manager.get("boss_attack12.png"),
        core.asset_manager.get("boss_attack13.png"),
        core.asset_manager.get("boss_attack14.png"),
        core.asset_manager.get("boss_attack15.png"),
        core.asset_manager.get("boss_attack16.png"),
        core.asset_manager.get("boss_attack17.png")
    ]

    attack_anim_speed = 0.05
    attack_anim_total_time = attack_anim_speed * len(attack_frames)
    attack_anim_frames_obj = AnimatedSpriteComp(attack_frames, animation_speed=attack_anim_speed, one_shot=True, offset_x=abs(base_animation_size[0]-attack_frames[0].get_size()[0])-3, offset_y=5)

    animated_character_cmp = AnimatedCharacterComp(base_animation_width=base_animation_size[0], base_animation_height=base_animation_size[1], idle_animated_sprite=idle_anim_frames_obj, hit_animated_sprite=hit_anim_frames_obj, attack_animated_sprite=attack_anim_frames_obj, moving_animated_sprite=moving_anim_frames_obj, current_animated_sprite=idle_anim_frames_obj, current_animation=AnimationType.IDLE)

    entity_manager.add_components(
        enemy_id, transform_cmp, render_cmp, physics_cmp, enemy_cmp,
        BossComp(attack_delay=8*attack_anim_speed, attack_cool_down=attack_anim_total_time+1, start_moving_delay=attack_anim_total_time),
        HealthComp(health=20), RectToDrawComp(), animated_character_cmp,
    )

    return enemy_id