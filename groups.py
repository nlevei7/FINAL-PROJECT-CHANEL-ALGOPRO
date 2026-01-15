from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface() 
        self.offset = pygame.Vector2()

#CAMERA 
    def draw(self, surface, offset):
        for sprite in self:
            surface.blit(sprite.image, sprite.rect.topleft - offset)