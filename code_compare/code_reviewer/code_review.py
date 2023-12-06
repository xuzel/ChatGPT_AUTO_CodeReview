import argparse
import torch
from code_compare.code_reviewer.configs import add_args
from code_compare.code_reviewer.models import ReviewerModel, build_or_load_gen_model

MAX_SOURCE_LENGTH = 512


def pad_assert(tokenizer, source_ids):
    source_ids = source_ids[:MAX_SOURCE_LENGTH - 2]
    source_ids = [tokenizer.bos_id] + source_ids + [tokenizer.eos_id]
    pad_len = MAX_SOURCE_LENGTH - len(source_ids)
    source_ids += [tokenizer.pad_id] * pad_len
    assert len(source_ids) == MAX_SOURCE_LENGTH, "Not equal length."
    return source_ids


def encode_diff(tokenizer, diff):
    difflines = diff.split("\n")[1:]  # remove start @@
    difflines = [line for line in difflines if len(line.strip()) > 0]
    map_dic = {"-": 0, "+": 1, " ": 2}

    def f(s):
        if s in map_dic:
            return map_dic[s]
        else:
            return 2

    labels = [f(line[0]) for line in difflines]
    difflines = [line[1:].strip() for line in difflines]
    inputstr = ""
    for label, line in zip(labels, difflines):
        if label == 1:
            inputstr += "<add>" + line
        elif label == 0:
            inputstr += "<del>" + line
        else:
            inputstr += "<keep>" + line
    source_ids = tokenizer.encode(inputstr, max_length=MAX_SOURCE_LENGTH, truncation=True)[1:-1]
    source_ids = pad_assert(tokenizer, source_ids)
    return source_ids


class CoseReview:
    def __init__(self):
        parser = argparse.ArgumentParser()
        args = add_args()
        args.model_name_or_path = "microsoft/codereviewer"
        self.config, self.model, self.tokenizer = build_or_load_gen_model(args)
        self.model.to("cuda")
        self.model.eval()

    def generate(self, code_diff: str) -> str:
        inputs = torch.tensor([encode_diff(self.tokenizer, code_diff)], dtype=torch.long).to("cuda")
        inputs_mask = inputs.ne(self.tokenizer.pad_id)
        preds = self.model.generate(inputs,
                                    attention_mask=inputs_mask,
                                    use_cache=True,
                                    num_beams=5,
                                    early_stopping=True,
                                    max_length=100,
                                    num_return_sequences=2
                                    )
        preds = list(preds.cpu().numpy())
        pred_nls = [self.tokenizer.decode(id[2:], skip_special_tokens=True, clean_up_tokenization_spaces=False) for id
                    in
                    preds]
        return pred_nls[0]
