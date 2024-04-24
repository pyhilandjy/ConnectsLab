import numpy as np

# from khaiii import KhaiiiApi
from wordcloud import WordCloud
from datetime import datetime
from pytz import timezone
import matplotlib.pyplot as plt

from konlpy.tag import Okt


class Tagger:
    def __init__(self, tagger=Okt):
        self.tagger = tagger

    def morphs(self, text):
        return self.tagger.morphs(text)

    # def remove_josa(self, text):
    #     """
    #     Removes not-so-useful morphs from the text.
    #     :param text:
    #     :return:
    #     """
    #     string = ""
    #     for word in self.khaiii.analyze(text):
    #         word_list = str(word).split()
    #         if "+" in word_list:
    #             for w in word_list[1:]:
    #                 if w == "+":
    #                     continue
    #                 josa_byebye = w.split("/")
    #                 if (
    #                     josa_byebye[1].startswith("J")
    #                     or josa_byebye[1].startswith("E")
    #                     or josa_byebye[1].startswith("X")
    #                 ):
    #                     continue
    #                 if josa_byebye[1].startswith("VX") or josa_byebye[1].startswith(
    #                     "S"
    #                 ):
    #                     continue
    #                 else:
    #                     if len(w.split("/")[0]) == 1:
    #                         continue
    #                     string += f"{w.split('/')[0]} "
    #         else:
    #             if len(word_list[0]) == 1:
    #                 continue
    #             string += f"{word_list[0]} "

    #     return string.strip()

    def names_dict(self):
        """
        extract the names of the speakers,
        returns dict with the names of the speakers as keys and their speech as values
        :return: names_dict
        """

        # # print(self.df[speaker_col_name].nunique)
        # self.num_speakers += self.df[self.speaker_col_name].nunique()

        name_dict = {}
        for idx in range(self.df.shape[0]):
            df_row = self.df.iloc[idx]
            if df_row[self.speaker_col_name] in name_dict.keys():
                name_dict[df_row[self.speaker_col_name]].extend(
                    df_row[self.contents_col_name].split()
                )
            else:
                name_dict[df_row[self.speaker_col_name]] = df_row[
                    self.contents_col_name
                ].split()
        return name_dict

    def circle_size(self, name_dict=None):
        cs = {}
        for speaker in name_dict.keys():
            cs[speaker] = [len(name_dict[speaker])]
        max_size = sum([list_[0] for list_ in cs.values()])
        for idx, list_ in enumerate(cs.values()):
            cs[list(cs.keys())[idx]].append(int(int(list_[0]) / max_size * 100))
        return cs

    def create_circle_mask(self, diameter):
        diameter = diameter * 10
        circle_mask = np.zeros(
            (diameter, diameter), dtype=np.uint8
        )  # Start with a black canvas
        center = np.array([diameter // 2, diameter // 2])
        radius = diameter // 2

        # Fill the circle with white (255)
        for y in range(diameter):
            for x in range(diameter):
                if np.linalg.norm([y - center[0], x - center[1]]) <= radius:
                    circle_mask[y, x] = 255
        return circle_mask

    def invert_mask(self, mask):
        return 255 - mask

    def create_wordcloud(
        self,
        name=None,
    ):
        time_serial = datetime.now(tz=timezone("Asia/Seoul")).strftime("%Y%m%d_%H%M%S")
        # print(self.num_speakers)
        if self.df[self.speaker_col_name].nunique() == 1:
            name_dict = self.names_dict()
            texts = {}
            for key, value in name_dict.items():
                text = " ".join(value)
                texts[key] = self.remove_josa(text)

            word_cloud = {}
            circle_size = self.circle_size(name_dict=name_dict)
            mask = self.create_circle_mask(circle_size[key][1])
            inverted_mask = self.invert_mask(mask)
            word_cloud[key] = WordCloud(
                background_color="white",
                width=circle_size[key][1] * 10,
                height=circle_size[key][1] * 10,
                mode="RGBA",
                max_words=100,
                mask=inverted_mask,
                font_path=self.font_path,
            ).generate(texts[key])
            fig, ax = plt.subplots(figsize=(12, 12))
            diameter = circle_size[key][1] * 10
            ax.imshow(
                word_cloud[key],
                interpolation="bilinear",
                extent=[-diameter / 2, diameter / 2, -diameter / 2, diameter / 2],
            )
            ax.axis("off")
            plt.tight_layout()
            plt.savefig(f"{name}_WordCloud_{time_serial}.png")
            plt.show()

        elif self.df[self.speaker_col_name].nunique() == 2:
            name_dict = self.names_dict()
            texts = {}
            for key, value in name_dict.items():
                text = " ".join(value)
                texts[key] = self.remove_josa(text)

            word_cloud = {}
            for key, value in texts.items():
                circle_size = self.circle_size(name_dict=name_dict)
                mask = self.create_circle_mask(circle_size[key][1])
                inverted_mask = self.invert_mask(mask)
                word_cloud[key] = WordCloud(
                    background_color="white",
                    width=circle_size[key][1] * 10,
                    height=circle_size[key][1] * 10,
                    mode="RGBA",
                    max_words=100,
                    mask=inverted_mask,
                    font_path=self.font_path,
                ).generate(value)

            # Plotting the word clouds vertically
            fig, axs = plt.subplots(2, 2, figsize=(12, 12))
            lim = 500
            axis_limits = (-1 * lim, lim, -1 * lim, lim)  # (xmin, xmax, ymin, ymax)

            # Wordcloud A (top)
            for idx, (key, wordcloud) in enumerate(word_cloud.items()):
                circle_size = self.circle_size(name_dict=name_dict)
                diameter = circle_size[key][1] * 10
                axs[idx][idx].imshow(
                    word_cloud[key],
                    interpolation="bilinear",
                    extent=[-diameter / 2, diameter / 2, -diameter / 2, diameter / 2],
                )
                axs[idx][idx].axis("off")
                axs[idx][idx].set_xlim(axis_limits[:2])
                axs[idx][idx].set_xlim(axis_limits[2:])

            axs[0][1].axis("off")
            axs[1][0].axis("off")

            plt.tight_layout()
            plt.savefig(f"{name}_WordCloud_{time_serial}.png")
            plt.show()

        else:
            print("number of speakers are more than 2")


# ----------------------------------------------------------
# path = '/content/drive/MyDrive/Colab Notebooks/ConnectsLab/response_1713763943096.json'
# khaiii_wc = KhaiiiWordCloud(path)
# khaiii_wc.create_wordcloud(name='test')
