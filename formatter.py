from pearl.core import Clip, PearlError
from colorama import Fore, Style


class Clip_Formatter:
    def __init__(self, clip):
        # If the parameter is not <Clip> class, raise PearlError
        if type(clip) != Clip:
            err = '<Clip_Formatter> only receives <core.Clip> class.'
            raise PearlError(err)

        self.movies = clip._data

    def print_clip(self):
        # Define frame
        top_frame = """
{title} | {grade} {genre}"
------------------------------------------------------
"""
        time_frame = """
{start} - {end} | {avail_cap} / {total_cap} | {cinfo} ({hinfo})
"""
        bottom_frame = """
------------------------------------------------------
"""
        # Remove whitespaces on the end
        top_frame = top_frame.strip()
        time_frame = time_frame.strip()
        bottom_frame = bottom_frame.strip()

        # Set <list> type variable `frame`
        frame = []

        # Draw table by adding strings on `frame`
        for movie in self.movies:
            # Add empty line
            frame.append('\n')

            # Colorize `TITLE` and draw top frame ::
            TITLE = \
                Fore.LIGHTBLUE_EX + Style.BRIGHT + \
                ' [' + movie + ']' + Style.RESET_ALL

            frame.append(top_frame.format(title=TITLE, grade=None, genre=None))

            # Draw time frame ::
            for sc in self.movies[movie]:
                # Colorize `start`, and add additional whitespace at front
                sc['start'] = \
                    Fore.LIGHTBLUE_EX + " " + sc['start'] + Style.RESET_ALL

                # Colorize `avail_cap` based on its value,
                # and format `avail_cap` into 3-digit-string
                if sc['avail_cap'] < int(sc['total_cap'] / 4):
                    # If avail_cap is below 25% of total capacity :: RED
                    sc['avail_cap'] = \
                        Fore.LIGHTRED_EX + \
                        "%3d" % sc['avail_cap'] + \
                        Style.RESET_ALL
                elif sc['avail_cap'] < int(sc['total_cap'] / 2):
                    # If avail_cap is below 50% of total capacity :: YELLOW
                    sc['avail_cap'] = \
                        Fore.LIGHTYELLOW_EX + \
                        "%3d" % sc['avail_cap'] + \
                        Style.RESET_ALL
                else:
                    sc['avail_cap'] = \
                        Fore.LIGHTBLUE_EX + \
                        "%3d" % sc['avail_cap'] + \
                        Style.RESET_ALL

                # Format `total_cap` into 3-digit-string
                sc['total_cap'] = "%3d" % sc['total_cap']

                # Append Item
                frame.append(time_frame.format(**sc))

            # Draw bottom frame and add few empty lines ::
            frame.append(bottom_frame)
            frame.append('\n')

        # Print data
        print('\n'.join(frame))
