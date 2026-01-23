resource "aws_instance" "my_ec2" {
  ami           = "ami-00e428798e77d38d9"
  instance_type = "t3a.medium"
  subnet_id     = "subnet-091a8716cb204b874"
  vpc_security_group_ids = [
    aws_security_group.instance_sg.id, # allow ALB -> instance traffic
    "sg-0e3fbebdccf513f8a"             # keep existing SG (optional)
  ]
  key_name             = "aws-access-key"
  iam_instance_profile = "ais-ec2-ssm-role"

  root_block_device {
    volume_type = "gp3"
    volume_size = 50
    iops        = 3000
    throughput  = 125
  }

  tags = {
    Name = "ais-api"
    Env  = var.env
  }
}

resource "aws_ebs_volume" "data_volume" {
  availability_zone = "us-east-2c"
  size              = 100
  type              = "gp3"

  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_volume_attachment" "data_volume_attachment" {
  device_name = "/dev/sdb"
  volume_id   = aws_ebs_volume.data_volume.id
  instance_id = aws_instance.my_ec2.id
}
