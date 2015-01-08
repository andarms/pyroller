from collections import OrderedDict
import pygame as pg
from ... import tools, prepare
from ...components import cards
from ...prepare import BROADCASTER as B
from .ui import *
import fysom
import json
import os


__all__ = ['Baccarat']

font_size = 64


class Baccarat(tools._State):
    """Baccarat game.  rules are configured in baccarat.json

    Rules were compiled by quick study on the Internet.  As expected, there is
    a considerable amount of variation on the stated rules, so artistic license
    was taken in determining what the rules should be.
    """

    # hack related to game states that do not finish
    did_startup = False

    def startup(self, now, persistent):
        self.now = now
        self.persist = persistent
        self.variation = "mini"
        self.load_json(os.path.join('resources', 'baccarat.json'))
        self.players = list()

        # stuff that might get moved to a gui layer sometime?
        self._background = None
        self._clicked_sprite = None

        # hack related to game states that do not finish
        self.done = False
        if self.did_startup:
            return
        self.did_startup = True

        self.casino_player = self.persist['casino_player']
        self.hud = pg.sprite.RenderUpdates()
        self.shoe = Deck((0, 0, 800, 600), decks=2)
        self.discard = Deck((0, 610, 0, 0), stacking=(0, 0))

        self.hud.add(ChipPile((0, 800, 800, 200)))

        b = NeonButton('lobby', (1000, 920, 0, 0), self.goto_lobby)
        self.hud.add(b)

    def load_json(self, filename):
        with open(filename) as fp:
            data = json.load(fp)

        config = data['baccarat'][self.variation]
        self.options = dict(config['options'])
        self.fsm = fysom.Fysom(**config['rules'])

    def goto_lobby(self):
        self.cash_out()
        self.done = True
        self.next = 'LOBBYSCREEN'

    def cash_out(self):
        pass

    def cleanup(self):
        return self.persist

    def get_event(self, event, scale=(1, 1)):
        # hack allows game to play before title
        if not self.did_startup:
            d = {'casino_player': None}
            self.startup(0, d)
            return

        # this music stuff really needs to be moved to the core
        # self.persist["music_handler"].get_event(event, scale)

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.goto_lobby()
                return

        elif event.type == pg.KEYUP:
            pass

        if event.type == pg.MOUSEMOTION:
            pos = tools.scaled_mouse_pos(scale)
            sprite = self._clicked_sprite
            if sprite is not None:
                sprite.pressed = sprite.rect.collidepoint(pos)

            for sprite in self.hud.sprites():
                if hasattr(sprite, 'on_mouse_enter'):
                    if sprite.rect.collidepoint(pos):
                        sprite.on_mouse_enter(pos)

                elif hasattr(sprite, 'on_mouse_leave'):
                    if not sprite.rect.collidepoint(pos):
                        sprite.on_mouse_leave(pos)

        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = tools.scaled_mouse_pos(scale)
            for sprite in self.hud.sprites():
                if hasattr(sprite, 'on_mouse_click'):
                    if sprite.rect.collidepoint(pos):
                        sprite.pressed = True
                        self._clicked_sprite = sprite

            for sprite in reversed(self.shoe.sprites()):
                if sprite.rect.collidepoint(pos):
                    # sprite.face_up = not sprite.face_up
                    self.shoe.remove(sprite)
                    self.discard.add(sprite)
                    # break so that cards under the clicked card are not picked
                    break

        elif event.type == pg.MOUSEBUTTONUP:
            pos = tools.scaled_mouse_pos(scale)
            sprite = self._clicked_sprite
            if sprite is not None:
                if sprite.rect.collidepoint(pos):
                    sprite.pressed = False
                    sprite.on_mouse_click(pos)
                self._clicked_sprite = None

    def update(self, surface, keys, current_time, dt, scale):
        if self._background is None:
            self._background = pg.Surface(surface.get_size())
            self._background.fill(prepare.BACKGROUND_BASE)
            surface.blit(self._background, (0, 0))

        self.discard.clear(surface, self._background)
        self.discard.draw(surface)
        self.shoe.clear(surface, self._background)
        self.shoe.draw(surface)
        self.hud.clear(surface, self._background)
        self.hud.draw(surface)

        # this music stuff really needs to be moved to the core
        # self.persist["music_handler"].update(scale)
        # self.persist["music_handler"].draw(surface)


class BaccaratState(object):
    def __init__(self, parent):
        self.parent = parent


class BeginState(BaccaratState):
    def get_event(self, event, scale=(1, 1)):
        pass

    def update(self, surface, keys, current_time, dt, scale):
        pass


class BetState(BaccaratState):
    def startup(self):
        B.linkEvent('bac-click-chip', self.on_chip)

    def cleanup(self):
        B.unlinkEvent('bac-click-chip', self.on_chip)

    def on_chip(self, *args):
        pass


class DealState(BaccaratState):
    def get_event(self, event, scale=(1, 1)):
        pass

    def update(self, surface, keys, current_time, dt, scale):
        pass


class ThreeOptionState(BaccaratState):
    def get_event(self, event, scale=(1, 1)):
        pass

    def update(self, surface, keys, current_time, dt, scale):
        pass


class FiveOptionState(BaccaratState):
    def get_event(self, event, scale=(1, 1)):
        pass

    def update(self, surface, keys, current_time, dt, scale):
        pass


class ClearTableState(BaccaratState):
    def get_event(self, event, scale=(1, 1)):
        pass

    def update(self, surface, keys, current_time, dt, scale):
        pass


class NewShoeState(BaccaratState):
    def get_event(self, event, scale=(1, 1)):
        pass

    def update(self, surface, keys, current_time, dt, scale):
        decks = self.options['decks']
        self.shoe.remove_all()
        self.shoe.add_decks(decks)
        self.discard.remove_all()


class EndState(BaccaratState):
    def get_event(self, event, scale=(1, 1)):
        pass

    def update(self, surface, keys, current_time, dt, scale):
        pass
