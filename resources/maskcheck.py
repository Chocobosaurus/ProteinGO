import pygame

def render_mask_on_image(image, mask, output_filename):
    masked_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    masked_image.blit(image, (0, 0))
    for y in range(mask.get_size()[1]):
        for x in range(mask.get_size()[0]):
            if mask.get_at((x, y)):
                pygame.draw.circle(masked_image, (255, 255, 255, 128), (x, y), 1)
    pygame.image.save(masked_image, output_filename)

image = pygame.image.load("protein_down1.png")
mask = pygame.mask.from_surface(image)
output_filename = "masked_image.png"
render_mask_on_image(image, mask, output_filename)
