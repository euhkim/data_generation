from utils import data_generator
from utils.conjugate import *
from utils.constituent_building import *
from utils.conjugate import *
from utils.randomize import choice
from utils.string_utils import string_beautify
from functools import reduce
from utils.vocab_sets import *


class AgreementGenerator(data_generator.BenchmarkGenerator):
    def __init__(self):
        super().__init__(field="morphology",
                         linguistics="subject_verb_agreement",
                         uid="irregular_plural_subj_v_agreement_2",
                         simple_lm_method=True,
                         one_prefix_method=False,
                         two_prefix_method=True,
                         lexically_identical=False)
        self.all_null_plural_nouns = get_all("sgequalspl", "1")
        self.all_missingPluralSing_nouns = get_all_conjunctive([("pluralform", ""), ("singularform", "")])
        self.all_unusable_nouns = np.union1d(self.all_null_plural_nouns, self.all_missingPluralSing_nouns)
        self.all_pluralizable_nouns = np.setdiff1d(all_common_nouns, self.all_unusable_nouns)
        self.all_irreg_nouns = get_all("irrpl", "1", self.all_pluralizable_nouns)
        self.all_reg_nouns = get_all("irrpl", "", self.all_pluralizable_nouns)

    def sample(self):
        # The cat       is        eating food
        # D   N1_agree  aux_agree V1     N2
        # The cats        is          eating food
        # D   N1_nonagree aux_agree V1     N2

        if random.choice([True, False]):
            V1 = choice(all_non_finite_transitive_verbs)
            try:
                N2 = N_to_DP_mutate(choice(get_matches_of(V1, "arg_2", all_nouns)))
            except TypeError:
                pass
        else:
            V1 = choice(all_non_finite_intransitive_verbs)
            N2 = " "
        try:
            N1_agree = choice(get_matches_of(V1, "arg_1", self.all_irreg_nouns))
        except TypeError:
                pass
        if N1_agree['sg'] == "1":
            N1_nonagree = N1_agree['pluralform']
        else:
            N1_nonagree = N1_agree['singularform']

        auxes = require_aux_agree(V1, N1_agree)
        aux_agree = auxes["aux_agree"]
        aux_nonagree = auxes["aux_nonagree"]

        data = {
            "sentence_good": "The %s %s %s %s." % (N1_agree[0], aux_agree, V1[0], N2[0]),
            "sentence_bad": "The %s %s %s %s." % (N1_nonagree, aux_agree, V1[0], N2[0]),
            "two_prefix_prefix_good": "The %s" % (N1_agree[0]),
            "two_prefix_prefix_bad": "The %s" % (N1_nonagree),
            "two_prefix_word": aux_agree
        }
        return data, data["sentence_good"]

generator = AgreementGenerator()
generator.generate_paradigm(rel_output_path="outputs/benchmark/%s.jsonl" % generator.uid, number_to_generate=10)
