from utils import data_generator
from utils.conjugate import *
from utils.constituent_building import *
from utils.conjugate import *
from utils.randomize import choice
from utils.string_utils import string_beautify


class CSCGenerator(data_generator.BenchmarkGenerator):
    def __init__(self):
        super().__init__(category="movement",
                         field="semantics",
                         linguistics="npi_licensing",
                         uid="npi_matrix_question_licensor_present",
                         simple_lm_method=True,
                         one_prefix_method=False,
                         two_prefix_method=True,
                         lexically_identical=True)
        self.safe_verbs = np.setdiff1d(all_non_finite_verbs, all_ing_verbs)


    def sample(self):
        # Have the teachers ever watched the waitresses?
        # Aux  Subj         EVER VP
        # The teachers have ever watched the waitresses.
        # Subj         Aux  EVER VP

        V = choice(self.safe_verbs)
        args = verb_args_from_verb(V)
        VP = V_to_VP_mutate(V, aux=False, args=args)

        data = {
            "sentence_good": "%s %s ever %s?" % (args["aux"][0], args["subj"][0], VP[0]),
            "sentence_bad": "%s %s ever %s." % (args["subj"][0], args["aux"][0], VP[0])
        }
        return data, data["sentence_good"]

generator = CSCGenerator()
generator.generate_paradigm(rel_output_path="outputs/benchmark/%s.jsonl" % generator.uid)
