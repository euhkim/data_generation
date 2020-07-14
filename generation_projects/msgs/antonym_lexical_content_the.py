
from utils import data_generator
from utils.constituent_building import *
from utils.conjugate import *
from utils.randomize import choice
import random
from generation_projects.msgs.antonym_helper import AntonymHelper
from utils.exceptions import *


# import generation_projects.msgs.person_helper

class MyGenerator(AntonymHelper):
    def __init__(self):
        super().__init__(uid="antonyms_lexical_content_the",
                         linguistic_feature_type="lexical semantics",
                         linguistic_feature_description="Does the sentence contain antonyms",
                         surface_feature_type="lexical_content",
                         surface_feature_description="Is the word \"the\" present?",
                         control_paradigm=False)
        self.the = get_all("expression", "the")
        self.safe_dets = np.setdiff1d(all_frequent_determiners, self.the)

    def sample(self):
        # Training 1
        # The man broke   a vase and the girl fixed       a car.
        # Subj1   Aux1 V1 Obj1   AND Subj2    Aux2 V1_ant Obj2

        # Training 0
        # The man broke   a vase and the girl destroyed     a car.
        # Subj1   Aux1 V1 Obj1   AND Subj2    Aux2 V1_other Obj2

        # Training 1
        # The man found   a vase and the girl lost        a car.
        # Subj1   Aux1 V2 Obj1   AND Subj2    Aux2 V2_ant Obj2

        # Training 0
        # The man found   a vase and the girl discovered    a car.
        # Subj1   Aux1 V2 Obj1   AND Subj2    Aux2 V2_other Obj2

        option = random.choice([1, 2])
        if option == 1:
            data, track_sentence = self.sample_verb()
        else:
            data, track_sentence = self.sample_adj()
        return data, track_sentence

    def sample_adj(self):
        V_trans = choice(all_transitive_verbs)
        NP_trans_1 = choice(get_matches_of(V_trans, "arg_1", all_common_nouns))
        NP_trans_2 = choice(get_matches_of(V_trans, "arg_2", all_common_nouns))
        D_trans_1 = choice(get_matched_by(NP_trans_1, "arg_1", self.safe_dets))
        D_trans_2 = choice(get_matched_by(NP_trans_2, "arg_1", self.safe_dets))
        Aux_trans = return_aux(V_trans, NP_trans_1)
        S1_abs = " ".join(["%s", NP_trans_1[0], Aux_trans[0], V_trans[0], "%s", NP_trans_2[0]])
        S1 = " ".join([D_trans_1[0], NP_trans_1[0], Aux_trans[0], V_trans[0], D_trans_2[0], NP_trans_2[0]])
        option = random.choice([1, 2])
        if option == 1:     # prenominal APs related by a transitive verb
            A1 = choice(self.in_domain_adjs_main)
            A1_ant = choice(get_all("expression", A1["antonym"], self.in_domain_adjs))
            A1_other = choice(get_all("expression", A1["synonym_hypernym_hyponym"], self.in_domain_adjs))
            try:
                Subj = choice(get_matches_of(A1, "arg_1", all_common_nouns))
            except Exception:
                pass
            Obj = choice(get_matches_of(A1_ant, "arg_1", get_matches_of(A1_other, "arg_1", all_common_nouns)))
            D1 = choice(get_matched_by(Subj, "arg_1", self.safe_dets))
            D2 = choice(get_matched_by(Obj, "arg_1", self.safe_dets))
            try:
                V = choice(get_matched_by(Subj, "arg_1", get_matched_by(Obj, "arg_2", all_transitive_verbs)))
            except Exception:
                raise MatchNotFoundError("fail to find verb with subj=%s and obj=%s" % (Subj[0], Obj[0]))
            Aux = return_aux(V, Subj, allow_negated=False)
            A2 = choice(get_matched_by(Subj, "arg_1", self.out_domain_adjs_main))
            try:
                A2_ant = choice(get_all("expression", A2["antonym"], self.out_domain_adjs))
                A2_other = choice(get_all("expression", A2["synonym_hypernym_hyponym"], self.out_domain_adjs))
            except Exception:
                pass
            if not (is_match_disj(Obj, A2_ant["arg_1"]) and is_match_disj(Obj, A2_other["arg_1"])):
                raise MatchNotFoundError("fail to match: %s %s %s %s %s " % (A2[0], A2_ant[0], A2_other[0], Subj[0], Obj[0]))

            Ds = []
            # Training_1_1
            if choice([True, False]):
                Ds.append(("the", D_trans_2[0], D1[0], D2[0]))
            else:
                Ds.append((D_trans_1[0], D_trans_2[0], D1[0], "the"))

            # Test_0_1
            if choice([True, False]):
                Ds.append((D_trans_1[0], "the", D1[0], D2[0]))
            else:
                Ds.append((D_trans_1[0], D_trans_2[0], "the", D2[0]))

            # Control_1_0
            if choice([True, False]):
                Ds.append((D_trans_1[0], "the", D1[0], D2[0]))
            else:
                Ds.append((D_trans_1[0], D_trans_2[0], "the", D2[0]))

            # Control_0_1
            if choice([True, False]):
                Ds.append((D_trans_1[0], "the", D1[0], D2[0]))
            else:
                Ds.append((D_trans_1[0], D_trans_2[0], "the", D2[0]))

            data = self.build_paradigm(
                training_1_1=" ".join([S1_abs, "and", "%s", A1[0], Subj[0], Aux[0], V[0], "%s", A1_ant[0], Obj[0], "."]) % Ds[0],
                training_0_0=" ".join([S1, "and", D1[0], A1[0], Subj[0], Aux[0], V[0], D2[0], A1_other[0], Obj[0], "."]),
                test_1_0=" ".join([S1, "and", D1[0], A2[0], Subj[0], Aux[0], V[0], D2[0], A2_ant[0], Obj[0], "."]),
                test_0_1=" ".join([S1_abs, "and", "%s", A2[0], Subj[0], Aux[0], V[0], "%s", A2_other[0], Obj[0], "."]) % Ds[1],
                control_1_1=" ".join([S1_abs, "and", "%s", A2[0], Subj[0], Aux[0], V[0], "%s", A2_ant[0], Obj[0], "."]) % Ds[2],
                control_0_0=" ".join([S1, "and", D1[0], A2[0], Subj[0], Aux[0], V[0], D2[0], A2_other[0], Obj[0], "."]),
                control_1_0=" ".join([S1, "and", D1[0], A1[0], Subj[0], Aux[0], V[0], D2[0], A1_ant[0], Obj[0], "."]),
                control_0_1=" ".join([S1_abs, "and", "%s", A1[0], Subj[0], Aux[0], V[0], "%s", A1_other[0], Obj[0], "."]) % Ds[3],
            )

            track_sentence = [
                (A1[0], Subj[0], V[0], A1_ant[0], Obj[0]),
                (A1[0], Subj[0], V[0], A1_other[0], Obj[0]),
                (A2[0], Subj[0], V[0], A2_ant[0], Obj[0]),
                (A2[0], Subj[0], V[0], A2_other[0], Obj[0]),
            ]
            return data, track_sentence
        else:      # predicative AP
            A1 = choice(self.in_domain_adjs_main)
            A1_ant = choice(get_all("expression", A1["antonym"], self.in_domain_adjs))
            A1_other = choice(get_all("expression", A1["synonym_hypernym_hyponym"], self.in_domain_adjs))
            Subj1 = choice(get_matches_of(A1, "arg_1", all_common_nouns))
            D1 = choice(get_matched_by(Subj1, "arg_1", self.safe_dets))
            Copula1 = return_copula(Subj1, allow_negated=False)
            A2 = choice(get_matched_by(Subj1, "arg_1", self.out_domain_adjs_main))
            A2_ant = choice(get_all("expression", A2["antonym"], self.out_domain_adjs))
            try:
                A2_other = choice(get_all("expression", A2["synonym_hypernym_hyponym"], self.out_domain_adjs))
            except Exception:
                pass
            Subj2 = choice(get_matches_of(A1_ant, "arg_1",
                                          get_matches_of(A1_other, "arg_1",
                                                         get_matches_of(A2_ant, "arg_1",
                                                                        get_matches_of(A2_other, "arg_1", all_common_nouns)))))
            D2 = choice(get_matched_by(Subj2, "arg_1", self.safe_dets))
            Copula2 = return_copula(Subj2, allow_negated=False)

            Ds = []
            # Training_1_1
            if choice([True, False]):
                Ds.append(("the", D_trans_2[0], D1[0], D2[0]))
            else:
                Ds.append((D_trans_1[0], D_trans_2[0], D1[0], "the"))

            # Test_0_1
            if choice([True, False]):
                Ds.append((D_trans_1[0], "the", D1[0], D2[0]))
            else:
                Ds.append((D_trans_1[0], D_trans_2[0], "the", D2[0]))

            # Control_1_1
            if choice([True, False]):
                Ds.append((D_trans_1[0], "the", D1[0], D2[0]))
            else:
                Ds.append((D_trans_1[0], D_trans_2[0], "the", D2[0]))

            # Control_0_1
            if choice([True, False]):
                Ds.append((D_trans_1[0], "the", D1[0], D2[0]))
            else:
                Ds.append((D_trans_1[0], D_trans_2[0], "the", D2[0]))

            data = self.build_paradigm(
                training_1_1=" ".join([S1_abs, "and", "%s", Subj1[0], Copula1[0], A1[0], "and", "%s", Subj2[0], Copula2[0], A1_ant[0], "."]) % Ds[0],
                training_0_0=" ".join([S1, "and", D1[0], Subj1[0], Copula1[0], A1[0], "and", D2[0], Subj2[0], Copula2[0], A1_other[0], "."]),
                test_1_0=" ".join([S1, "and", D1[0], Subj1[0], Copula1[0], A2[0], "and", D2[0], Subj2[0], Copula2[0], A2_ant[0], "."]),
                test_0_1=" ".join([S1_abs, "and", "%s", Subj1[0], Copula1[0], A2[0], "and", "%s", Subj2[0], Copula2[0], A2_other[0], "."]) % Ds[1],
                control_1_1=" ".join([S1_abs, "and", "%s", Subj1[0], Copula1[0], A2[0], "and", "%s", Subj2[0], Copula2[0], A2_ant[0], "."]) % Ds[2],
                control_0_0=" ".join([S1, "and", D1[0], Subj1[0], Copula1[0], A2[0], "and", D2[0], Subj2[0], Copula2[0], A2_other[0], "."]),
                control_1_0=" ".join([S1, "and", D1[0], Subj1[0], Copula1[0], A1[0], "and", D2[0], Subj2[0], Copula2[0], A1_ant[0], "."]),
                control_0_1=" ".join([S1_abs, "and", "%s", Subj1[0], Copula1[0], A1[0], "and", "%s", Subj2[0], Copula2[0], A1_other[0], "."]) % Ds[3],
            )
            track_sentence = [
                (A1[0], Subj1[0], A1_ant[0], Subj2[0]),
                (A1[0], Subj1[0], A1_other[0], Subj2[0]),
                (A1[0], Subj1[0], A2_ant[0], Subj2[0]),
                (A1[0], Subj1[0], A2_other[0], Subj2[0]),
            ]
            return data, track_sentence

    def sample_verb(self):
        V_trans = choice(all_transitive_verbs)
        NP_trans_1 = choice(get_matches_of(V_trans, "arg_1", all_common_nouns))
        NP_trans_2 = choice(get_matches_of(V_trans, "arg_2", all_common_nouns))
        D_trans_1 = choice(get_matched_by(NP_trans_1, "arg_1", self.safe_dets))
        D_trans_2 = choice(get_matched_by(NP_trans_2, "arg_1", self.safe_dets))
        Aux_trans = return_aux(V_trans, NP_trans_1)
        S1_abs = " ".join(["%s", NP_trans_1[0], Aux_trans[0], V_trans[0], "%s", NP_trans_2[0]])
        S1 = " ".join([D_trans_1[0], NP_trans_1[0], Aux_trans[0], V_trans[0], D_trans_2[0], NP_trans_2[0]])
        V1 = choice(self.in_domain_verbs_main)
        try:
            V1_ant = get_same_V_form(V1["antonym"], V1)
            V1_other = get_same_V_form(V1["synonym_hypernym_hyponym"], V1)
        except Exception:
            pass
        Subj1 = choice(get_matches_of(V1, "arg_1", get_matches_of(V1_ant, "arg_1", get_matches_of(V1_other, "arg_1", all_common_nouns))))
        Subj2 = choice(get_matches_of(V1_ant, "arg_1", get_matches_of(V1_other, "arg_1", all_common_nouns)))
        D1 = choice(get_matched_by(Subj1, "arg_1", self.safe_dets))
        D2 = choice(get_matched_by(Subj2, "arg_1", self.safe_dets))
        Aux1 = return_aux(V1, Subj1, allow_negated=False)
        Aux2 = return_aux(V1_ant, Subj2, allow_negated=False)
        if V1["category"] == "(S\\NP)/NP":  # If the antonym is transitive, we need to generate objects that match all relevant verb forms
            for _ in range(10):
                Obj1 = N_to_DP_mutate(choice(get_matches_of(V1, "arg_2", get_matches_of(V1_ant, "arg_2",
                                                                                        get_matches_of(V1_other, "arg_2", all_nouns)))), avoid=self.the)
                Obj2 = N_to_DP_mutate(choice(get_matches_of(V1, "arg_2", get_matches_of(V1_ant, "arg_2",
                                                                                        get_matches_of(V1_other, "arg_2", all_nouns)))), avoid=self.the)
                try:
                    V2 = choice(get_matches_of(Aux1, "arg_2", get_matched_by(Subj1, "arg_1",
                                                                             get_matched_by(Obj1, "arg_2",
                                                                                            self.out_domain_transitive_verbs_main))))
                except Exception:
                    raise MatchNotFoundError("fail to find V: %s %s %s %s %s" % (V1[0], Subj1[0], Subj2[0], Obj1[0], Obj2[0]))
                V2 = get_same_V_form(V2["root"], V1)
                V2_ant = get_same_V_form(V2["antonym"], V2)
                V2_other = get_same_V_form(V2["synonym_hypernym_hyponym"], V2)
                if is_match_disj(Obj2, V2_ant["arg_2"]) and is_match_disj(Obj2, V2_other["arg_2"]) and \
                        is_match_disj(Subj2, V2_ant["arg_1"]) and is_match_disj(Subj2, V2_other["arg_1"]):
                    break
                else:
                    print("fail to match: %s %s %s %s %s %s" % (V1[0], V2[0], Subj1[0], Subj2[0], Obj1[0], Obj2[0]))
        elif V1["category"] == "S\\NP":  # If the antonym is intransitive, no objects
            try:
                V2 = choice(get_matches_of(Aux1, "arg_2",
                                           get_matched_by(Subj1, "arg_1", self.out_domain_intransitive_verbs_main)))
            except Exception:
                raise MatchNotFoundError("fail to find V: %s %s %s" % (V1[0], Subj1[0], Subj2[0]))
            V2 = get_same_V_form(V2["root"], V1)
            V2_ant = get_same_V_form(V2["antonym"], V2)
            V2_other = get_same_V_form(V2["synonym_hypernym_hyponym"], V2)
            Obj1 = self.empty  # No object: this is an empty string
            Obj2 = self.empty  # No object: this is an empty string
            if is_match_disj(Subj2, V2_ant["arg_1"]) and is_match_disj(Subj2, V2_other["arg_1"]):
                pass
            else:
                raise MatchNotFoundError("fail to match: %s %s %s %s" % (V1[0], V2[0], Subj1[0], Subj2[0]))

        Ds = []
        if choice([True, False]):
            Ds.append(("the", D_trans_2[0], D1[0], D2[0]))
        else:
            Ds.append((D_trans_1[0], D_trans_2[0], D1[0], "the"))

        if choice([True, False]):
            Ds.append((D_trans_1[0], "the", D1[0], D2[0]))
        else:
            Ds.append((D_trans_1[0], D_trans_2[0], "the", D2[0]))

        if choice([True, False]):
            Ds.append((D_trans_1[0], "the", D1[0], D2[0]))
        else:
            Ds.append((D_trans_1[0], D_trans_2[0], "the", D2[0]))

        if choice([True, False]):
            Ds.append((D_trans_1[0], "the", D1[0], D2[0]))
        else:
            Ds.append((D_trans_1[0], D_trans_2[0], "the", D2[0]))

        data = self.build_paradigm(
            training_1_1=" ".join([S1_abs, "and", "%s", Subj1[0], Aux1[0], V1[0], Obj1[0], "and", "%s", Subj2[0], Aux2[0], V1_ant[0], Obj2[0], "."]) % Ds[0],
            training_0_0=" ".join([S1, "and", D1[0], Subj1[0], Aux1[0], V1[0], Obj1[0], "and", D2[0], Subj2[0], Aux2[0], V1_other[0], Obj2[0], "."]),
            test_1_0=" ".join([S1, "and", D1[0], Subj1[0], Aux1[0], V2[0], Obj1[0], "and", D2[0], Subj2[0], Aux2[0], V2_ant[0], Obj2[0], "."]),
            test_0_1=" ".join([S1_abs, "and", "%s", Subj1[0], Aux1[0], V2[0], Obj1[0], "and", "%s", Subj2[0], Aux2[0], V2_other[0], Obj2[0], "."]) % Ds[1],
            control_1_1=" ".join([S1_abs, "and", "%s", Subj1[0], Aux1[0], V2[0], Obj1[0], "and", "%s", Subj2[0], Aux2[0], V2_ant[0], Obj2[0], "."]) % Ds[2],
            control_0_0=" ".join([S1, "and", D1[0], Subj1[0], Aux1[0], V2[0], Obj1[0], "and", D2[0], Subj2[0], Aux2[0], V2_other[0], Obj2[0], "."]),
            control_1_0=" ".join([S1, "and", D1[0], Subj1[0], Aux1[0], V1[0], Obj1[0], "and", D2[0], Subj2[0], Aux2[0], V1_ant[0], Obj2[0], "."]),
            control_0_1=" ".join([S1_abs, "and", "%s", Subj1[0], Aux1[0], V1[0], Obj1[0], "and", "%s", Subj2[0], Aux2[0], V1_other[0], Obj2[0], "."]) % Ds[3],
        )
        track_sentence = [
            (Subj1[0], V1[0], Obj1[0], Subj2[0], V1_ant[0], Obj2[0], "."),
            (Subj1[0], V1[0], Obj1[0], Subj2[0], V1_other[0], Obj2[0], "."),
            (Subj1[0], V2[0], Obj1[0], Subj2[0], V2_ant[0], Obj2[0], "."),
            (Subj1[0], V2[0], Obj1[0], Subj2[0], V2_ant[0], Obj2[0], "."),
        ]
        return data, track_sentence

generator = MyGenerator()
generator.generate_paradigm(number_to_generate=5000, rel_output_path="outputs/msgs/" + generator.uid)