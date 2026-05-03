from platformio.managers.platform import PlatformBase

class Air105Platform(PlatformBase):
    def is_embedded(self):
        return True

    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_dynamic_options(result)
        else:
            for key, value in result.items():
                result[key] = self._add_dynamic_options(result[key])
        return result

    def _add_dynamic_options(self, board):
        if not board.get("upload.protocols", []):
            board.manifest["upload"]["protocols"] = ["mhboot"]
        if not board.get("upload.protocol", ""):
            board.manifest["upload"]["protocol"] = "mhboot"
        return board
