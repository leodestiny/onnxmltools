# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ....common._registration import register_converter


def convert_padding(scope, operator, container):
    op_type = 'Pad'
    attrs = {'name': operator.full_name}
    params = operator.raw_operator.padding

    pad_table = {'constant': 'constant', 'reflection': 'reflect', 'replication': 'edge'}
    pad_type = params.WhichOneof('PaddingType')
    if pad_type not in pad_table:
        raise ValueError('Unsupported padding mode: {}'.format(pad_type))
    attrs['mode'] = pad_table[pad_type]

    # CoreML only pads for their H- and W-axes. Here we assume the shape of the tensor to be padded
    # is [N, C, H, W], so we have 8 padding amounts
    #     pads = [N_begin_index, C_begin_index, H_begin_index, W_begin_index,
    #             N_end_index,   C_end_index,   H_end_index,   W_end_index]
    # Because only H- and W-axes are padded in CoreML, we leave padding amounts of N- and C-axes zeros.
    pads = [0, 0, 0, 0, 0, 0, 0, 0]
    if len(params.paddingAmounts.borderAmounts) > 0:
        # Set H_begin_index
        pads[2] = params.paddingAmounts.borderAmounts[0].startEdgeSize
        # Set W_begin_index
        pads[3] = params.paddingAmounts.borderAmounts[1].startEdgeSize
        # Set H_end_index
        pads[6] = params.paddingAmounts.borderAmounts[0].endEdgeSize
        # Set W_end_index
        pads[7] = params.paddingAmounts.borderAmounts[1].endEdgeSize
    attrs['pads'] = pads

    if pad_type == 'constant':
        attrs['value'] = params.constant.value

    container.add_node(op_type, operator.input_full_names, operator.output_full_names, op_version=2, **attrs)


register_converter('padding', convert_padding)
