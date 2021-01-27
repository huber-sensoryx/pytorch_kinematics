import math

import torch
import pytorch_kinematics as pk


def quat_pos_from_transform3d(tg):
    m = tg.get_matrix()
    pos = m[:, :3, 3]
    rot = pk.matrix_to_quaternion(m[:, :3, :3])
    return pos, rot


def test_fkik():
    data = '<robot name="test_robot">' \
           '<link name="link1" />' \
           '<link name="link2" />' \
           '<link name="link3" />' \
           '<joint name="joint1" type="revolute">' \
           '<origin xyz="1.0 0.0 0.0"/>' \
           '<parent link="link1"/>' \
           '<child link="link2"/>' \
           '</joint>' \
           '<joint name="joint2" type="revolute">' \
           '<origin xyz="1.0 0.0 0.0"/>' \
           '<parent link="link2"/>' \
           '<child link="link3"/>' \
           '</joint>' \
           '</robot>'
    chain = pk.build_serial_chain_from_urdf(data, 'link3')
    th1 = torch.tensor([0.42553542, 0.17529176])
    tg = chain.forward_kinematics(th1)
    pos, rot = quat_pos_from_transform3d(tg)
    assert torch.allclose(pos, torch.tensor([[1.91081784, 0.41280851, 0.0000]]))
    assert torch.allclose(rot, torch.tensor([[0.95521418, 0.0000, 0.0000, 0.2959153]]))
    print(tg)
    # TODO implement and test inverse kinematics
    # th2 = chain.inverse_kinematics(tg)
    # self.assertTrue(np.allclose(th1, th2, atol=1.0e-6))
    # test batch kinematics
    N = 20
    th_batch = torch.rand(N, 2)
    tg_batch = chain.forward_kinematics(th_batch)
    m = tg_batch.get_matrix()
    for i in range(N):
        tg = chain.forward_kinematics(th_batch[i])
        assert torch.allclose(tg.get_matrix().view(4, 4), m[i])


# test robot with prismatic and fixed joints
def test_fk_simple_arm():
    chain = pk.build_chain_from_sdf(open("simple_arm.sdf").read())
    # print(chain)
    # print(chain.get_joint_parameter_names())
    ret = chain.forward_kinematics({'arm_elbow_pan_joint': math.pi / 2.0, 'arm_wrist_lift_joint': -0.5})
    tg = ret['arm_wrist_roll']
    pos, rot = quat_pos_from_transform3d(tg)
    assert torch.allclose(rot, torch.tensor([0.70710678, 0., 0., 0.70710678]))
    assert torch.allclose(pos, torch.tensor([1.05, 0.55, 0.5]))


# test more complex robot and the MJCF parser
def test_fk_mjcf():
    chain = pk.build_chain_from_mjcf(open("ant.xml").read())
    print(chain)
    print(chain.get_joint_parameter_names())
    th = {'hip_1': 1.0, 'ankle_1': 1}
    ret = chain.forward_kinematics(th)
    tg = ret['aux_1_child']
    pos, rot = quat_pos_from_transform3d(tg)
    assert torch.allclose(rot, torch.tensor([0.87758256, 0., 0., 0.47942554]))
    assert torch.allclose(pos, torch.tensor([0.2, 0.2, 0.75]))
    tg = ret['front_left_foot_child']
    pos, rot = quat_pos_from_transform3d(tg)
    assert torch.allclose(rot, torch.tensor([0.77015115, -0.4600326, 0.13497724, 0.42073549]))
    assert torch.allclose(pos, torch.tensor([0.13976626, 0.47635466, 0.75]))
    print(ret)


def test_fk_mjcf_humanoid():
    chain = pk.build_chain_from_mjcf(open("humanoid.xml").read())
    print(chain)
    print(chain.get_joint_parameter_names())
    th = {'left_knee': 0.0, 'right_knee': 0.0}
    ret = chain.forward_kinematics(th)
    print(ret)


if __name__ == "__main__":
    test_fkik()
    test_fk_simple_arm()
    test_fk_mjcf()
    # test_fk_mjcf_humanoid()
